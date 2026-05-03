# youtube2mp3_model.py
import os
import json
import datetime
import requests
from pytubefix import YouTube

# Adaptador de BD — importación segura
try:
    import sys as _sys
    _src = os.path.dirname(__file__)
    if _src not in _sys.path:
        _sys.path.insert(0, _src)
    from model.db_adapter import upsert_cancion, registrar_descarga
    _DB_ADAPTER_OK = True
except Exception as _db_e:
    print(f"⚠️ youtube2mp3_model: db_adapter no disponible ({_db_e})")
    _DB_ADAPTER_OK = False

# Intentar múltiples bibliotecas de audio para conversión
HAS_CONVERSION = False
CONVERTER_TYPE = None

try:
    from moviepy.editor import AudioFileClip
    HAS_CONVERSION = True
    CONVERTER_TYPE = "moviepy"
    print("✅ Usando moviepy para conversión de audio de YouTube")
except ImportError:
    try:
        from pydub import AudioSegment
        HAS_CONVERSION = True
        CONVERTER_TYPE = "pydub"
        print("✅ Usando pydub para conversión de audio de YouTube")
    except ImportError:
        HAS_CONVERSION = False
        print("⚠️ No hay bibliotecas de conversión disponibles. Solo cambio de extensión.")
        print("   Instala moviepy: pip install moviepy")
        print("   O instala pydub: pip install pydub")

# Intentar importar bibliotecas para metadatos de audio
HAS_METADATA = False
METADATA_TYPE = None

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3
    from mutagen.id3._frames import APIC, TIT2, TPE1, TALB
    HAS_METADATA = True
    METADATA_TYPE = "mutagen"
    print("✅ Usando mutagen para metadatos de audio de YouTube")
except ImportError:
    try:
        import eyed3
        HAS_METADATA = True
        METADATA_TYPE = "eyed3"
        print("✅ Usando eyed3 para metadatos de audio")
    except ImportError:
        HAS_METADATA = False
        print("⚠️ Sin bibliotecas de metadatos. Las portadas no se incrustarán.")
        print("   Instala mutagen: pip install mutagen")
        print("   O instala eyed3: pip install eyed3")


class YouTube2MP3Converter:
    def __init__(self):
        self.origin = "YouTube"

    @staticmethod
    def download_video(url):
        # Crear carpeta de descargas si no existe
        downloads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "music")
        os.makedirs(downloads_dir, exist_ok=True)
        
        try:
            yt = YouTube(url)
            print(f"Título: {yt.title}")
            print(f"Autor: {yt.author}")
            
            # Primero intentar obtener streams de audio de mejor calidad
            audio_streams = yt.streams.filter(only_audio=True).order_by('abr').desc()
            
            if not audio_streams:
                raise Exception("No se encontraron streams de audio disponibles")
            
            # Preferir M4A o MP4 que suelen tener mejor compatibilidad
            preferred_stream = None
            for stream in audio_streams:
                if stream.mime_type in ['audio/mp4', 'audio/webm']:
                    preferred_stream = stream
                    break
            
            if not preferred_stream:
                preferred_stream = audio_streams.first()
            
            print(f"Descargando stream: {preferred_stream.mime_type} - {preferred_stream.abr}") # type: ignore
            out_file = preferred_stream.download(output_path=downloads_dir) # type: ignore
            
            # Extraer todos los metadatos disponibles de YouTube
            keywords = []
            try:
                keywords = yt.keywords or []
            except Exception:
                pass

            publish_date = None
            try:
                if yt.publish_date:
                    publish_date = yt.publish_date.isoformat()
            except Exception:
                pass

            video_info = {
                'file_path':     out_file,
                'title':         yt.title,
                'author':        yt.author,
                'thumbnail_url': yt.thumbnail_url,
                'length':        yt.length,
                'video_id':      yt.video_id,
                'channel_url':   yt.channel_url,
                'description':   (yt.description or '').strip(),
                'keywords':      keywords,
                'publish_date':  publish_date,
                'views':         yt.views,
            }
            
            return video_info
            
        except Exception as e:
            raise Exception(f"Error al descargar el video: {e}")

    @staticmethod
    def download_thumbnail(thumbnail_url, save_path):
        """Descarga la thumbnail del video"""
        try:
            print("🖼️ Descargando portada del video...")
            response = requests.get(thumbnail_url, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Portada descargada: {save_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando portada: {e}")
            return False

    @staticmethod
    def add_metadata_to_mp3(mp3_path, title, artist, thumbnail_path=None, origin="YouTube",
                             album="", year="", genre="", comment=""):
        """Añade metadatos al archivo MP3 incluyendo la portada y origen"""
        try:
            if not HAS_METADATA:
                print("⚠️ Sin bibliotecas de metadatos disponibles")
                return False

            # Verificar que el archivo MP3 existe y tiene contenido
            if not os.path.exists(mp3_path):
                print(f"❌ El archivo MP3 no existe: {mp3_path}")
                return False
                
            if os.path.getsize(mp3_path) == 0:
                print(f"❌ El archivo MP3 está vacío: {mp3_path}")
                return False

            print("🏷️ Añadiendo metadatos al MP3...")
            
            if METADATA_TYPE == "mutagen":
                # Usar mutagen - con verificación de archivo válido
                from mutagen.mp3 import MP3
                from mutagen.id3 import ID3, APIC, TIT2, TPE1, TXXX # type: ignore
                
                try:
                    # Cargar el archivo MP3 con validación
                    audio_file = MP3(mp3_path, ID3=ID3)
                    
                    # Verificar que se pudo cargar correctamente
                    if audio_file.info is None:
                        print("❌ El archivo MP3 no es válido o está corrupto")
                        return False
                        
                    print(f"📊 Duración del MP3: {audio_file.info.length:.1f} segundos")
                    
                except Exception as e:
                    print(f"❌ Error cargando archivo MP3: {e}")
                    print("🔧 Intentando reparar/recrear metadatos...")
                    
                    # Intentar crear un objeto MP3 básico
                    try:
                        audio_file = MP3(mp3_path)
                        if audio_file.tags is None:
                            audio_file.add_tags()
                    except Exception as repair_error:
                        print(f"❌ No se pudo reparar el archivo: {repair_error}")
                        return False
                
                # Añadir ID3 tag si no existe
                if audio_file.tags is None:
                    audio_file.add_tags()
                
                # Añadir metadatos completos
                from mutagen.id3 import COMM, TALB, TDRC, TCON  # type: ignore
                audio_file.tags.add(TIT2(encoding=3, text=title))   # type: ignore  # Título
                audio_file.tags.add(TPE1(encoding=3, text=artist))  # type: ignore  # Artista
                if album:
                    audio_file.tags.add(TALB(encoding=3, text=album))   # type: ignore  # Álbum
                if year:
                    audio_file.tags.add(TDRC(encoding=3, text=str(year)))  # type: ignore  # Año
                if genre:
                    audio_file.tags.add(TCON(encoding=3, text=genre))   # type: ignore  # Género

                # Comentario con origen y descripción
                comment_text = comment if comment else f"Origen: {origin}"
                audio_file.tags.add(COMM(  # type: ignore
                    encoding=3,
                    lang='spa',
                    desc='',
                    text=[comment_text]
                ))
                
                # Añadir portada si está disponible
                if thumbnail_path and os.path.exists(thumbnail_path):
                    try:
                        with open(thumbnail_path, 'rb') as img:
                            image_data = img.read()
                            if len(image_data) > 0:
                                audio_file.tags.add(APIC( # type: ignore
                                    encoding=3,  # UTF-8
                                    mime='image/jpeg',  # MIME type
                                    type=3,  # Cover (front)
                                    desc='Cover',
                                    data=image_data
                                ))
                                print(f"✅ Portada incrustada ({len(image_data)} bytes)")
                            else:
                                print("⚠️ Archivo de portada vacío")
                    except Exception as img_error:
                        print(f"⚠️ Error añadiendo portada: {img_error}")
                else:
                    print("ℹ️ No hay portada para añadir")
                
                # Guardar cambios con manejo de errores
                try:
                    audio_file.save()
                    print(f"✅ Metadatos añadidos correctamente (Origen: {origin})")
                    return True
                except Exception as save_error:
                    print(f"❌ Error guardando metadatos: {save_error}")
                    return False
                
            elif METADATA_TYPE == "eyed3":
                # Usar eyed3 con verificación similar
                import eyed3
                
                try:
                    audio_file = eyed3.load(mp3_path)
                    if audio_file is None:
                        print("❌ El archivo MP3 no es válido para eyed3")
                        return False
                        
                    if audio_file.tag is None:
                        audio_file.initTag()
                    
                    # Añadir metadatos completos
                    audio_file.tag.title = title
                    audio_file.tag.artist = artist
                    if album:
                        audio_file.tag.album = album
                    if year:
                        audio_file.tag.recording_date = eyed3.core.Date(int(year[:4]))
                    if genre:
                        audio_file.tag.genre = genre

                    # Comentario con origen y descripción
                    comment_text = comment if comment else f"Origen: {origin}"
                    audio_file.tag.comments.set(comment_text) # type: ignore
                    
                    # Añadir portada
                    if thumbnail_path and os.path.exists(thumbnail_path):
                        try:
                            with open(thumbnail_path, 'rb') as img:
                                image_data = img.read()
                                audio_file.tag.images.set(3, image_data, 'image/jpeg') # type: ignore
                                print(f"✅ Portada incrustada ({len(image_data)} bytes)")
                        except Exception as img_error:
                            print(f"⚠️ Error añadiendo portada: {img_error}")
                    
                    audio_file.tag.save() # type: ignore
                    print(f"✅ Metadatos añadidos correctamente (Origen: {origin})")
                    return True
                    
                except Exception as e:
                    print(f"❌ Error con eyed3: {e}")
                    return False
            
            return False
            
        except Exception as e:
            print(f"❌ Error crítico añadiendo metadatos: {e}")
            import traceback
            print(f"📋 Detalles: {traceback.format_exc()}")
            return False

    @staticmethod
    def convert_to_mp3(file_path):
        """Convierte el archivo de audio descargado a MP3"""
        try:
            # Obtener información del archivo
            base_name = os.path.splitext(file_path)[0]
            file_ext = os.path.splitext(file_path)[1].lower()
            mp3_path = base_name + ".mp3"
            
            print(f"🔄 Archivo a convertir: {file_path}")
            print(f"📁 Extensión detectada: {file_ext}")
            print(f"🎯 Ruta MP3 objetivo: {mp3_path}")
            
            # Si ya es MP3, no convertir
            if file_ext == '.mp3':
                print("✅ El archivo ya es MP3")
                return file_path
            
            print(f"🔄 Convirtiendo {file_ext} a MP3...")
            
            conversion_success = False
            
            # Intentar moviepy primero (más confiable)
            if HAS_CONVERSION and CONVERTER_TYPE == "moviepy":
                try:
                    print("🎬 Usando moviepy para conversión...")
                    from moviepy.editor import AudioFileClip
                    
                    audio_clip = AudioFileClip(file_path)
                    audio_clip.write_audiofile(mp3_path, verbose=False, logger=None)
                    audio_clip.close()
                    
                    # Verificar que el archivo se creó correctamente
                    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                        os.remove(file_path)  # Eliminar original
                        print("✅ Conversión completada con moviepy")
                        conversion_success = True
                        return mp3_path
                    else:
                        print("❌ Archivo MP3 no se creó correctamente con moviepy")
                        
                except Exception as e:
                    print(f"❌ Error con moviepy: {e}")
            
            # Intentar pydub como segunda opción
            if not conversion_success and HAS_CONVERSION and CONVERTER_TYPE == "pydub":
                try:
                    print("🎵 Usando pydub para conversión...")
                    from pydub import AudioSegment
                    
                    if file_ext == '.webm':
                        audio = AudioSegment.from_file(file_path, format="webm")
                    elif file_ext in ['.mp4', '.m4a']:
                        audio = AudioSegment.from_file(file_path, format="mp4")
                    else:
                        audio = AudioSegment.from_file(file_path)
                    
                    audio.export(mp3_path, format="mp3", bitrate="192k")
                    
                    # Verificar que el archivo se creó correctamente
                    if os.path.exists(mp3_path) and os.path.getsize(mp3_path) > 0:
                        os.remove(file_path)  # Eliminar original
                        print("✅ Conversión completada con pydub")
                        conversion_success = True
                        return mp3_path
                    else:
                        print("❌ Archivo MP3 no se creó correctamente con pydub")
                        
                except Exception as e:
                    print(f"❌ Error con pydub: {e}")
            
            # Si no se pudo convertir con bibliotecas especializadas
            if not conversion_success:
                print("⚠️ Sin bibliotecas de conversión disponibles o falló la conversión")
                print("📝 Usando conversión simple (cambio de extensión)")
                print("💡 Para conversión real, instala: pip install moviepy")
                
                # Cambio de extensión como fallback
                if file_path != mp3_path:
                    os.rename(file_path, mp3_path)
                    print(f"✅ Archivo renombrado a: {mp3_path}")
                    print("ℹ️ NOTA: Este es solo un cambio de extensión.")
                    print("ℹ️ Para conversión real del contenido, instala moviepy.")
                else:
                    print("ℹ️ El archivo ya tiene el nombre correcto")
                
            return mp3_path
            
        except Exception as e:
            print(f"❌ Error crítico en la conversión: {e}")
            import traceback
            traceback.print_exc()
            return file_path

    def _save_metadata_to_json(self, video_info: dict, mp3_path: str) -> None:
        """Guarda los metadatos de YouTube en data/metadata/youtube_metadata.json,
        con la misma estructura que spotify_metadata.json."""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            metadata_dir = os.path.join(project_root, 'data', 'metadata')
            os.makedirs(metadata_dir, exist_ok=True)
            filepath = os.path.join(metadata_dir, 'youtube_metadata.json')

            keywords = video_info.get('keywords') or []
            genre_str = ', '.join(keywords[:5]) if keywords else ''

            track_data = {
                'titulo':           video_info.get('title', ''),
                'artista':          video_info.get('author', ''),
                'album':            '',
                'duracion_seg':     video_info.get('length') or 0,
                'genero':           genre_str,
                'plataforma_origen': 'YouTube',
                'url_origen':       video_info.get('url_origen', ''),
                'ruta_local':       mp3_path,
                'caratula_url':     video_info.get('thumbnail_url', ''),
                'letra':            '',
                'video_id':         video_info.get('video_id', ''),
                'channel_url':      video_info.get('channel_url', ''),
                'description':      video_info.get('description', ''),
                'keywords':         keywords,
                'publish_date':     video_info.get('publish_date', ''),
                'views':            video_info.get('views', 0),
                'fecha_extraccion': datetime.datetime.now().isoformat(),
            }

            # Cargar existente o crear nuevo
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except Exception:
                    data = {'tracks': []}
            else:
                data = {'tracks': []}

            data['tracks'].append(track_data)
            data['track_actual'] = track_data
            data['ultima_actualizacion'] = datetime.datetime.now().isoformat()
            data['total_tracks'] = len(data['tracks'])
            data['tipo_descarga'] = 'cancion_individual'

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"💾 Metadatos YouTube guardados: {filepath}")
        except Exception as e:
            print(f"⚠️ Error guardando metadatos YouTube: {e}")

    def convert(self, url):
        """Descarga y convierte el video de YouTube a MP3 con portada"""
        try:
            print(f"🔄 Descargando: {url}")
            
            # Auto-detect source from URL
            source = "youtube" if "youtube" in url.lower() or "youtu.be" in url.lower() else "unknown"
            print(f"📍 Fuente detectada: {source}")
            
            video_info = self.download_video(url)
            video_info['url_origen'] = url  # guardar URL original para metadatos
            print(f"📁 Archivo descargado: {video_info['file_path']}")
            
            print(f"🔄 Convirtiendo a MP3...")
            mp3_file = self.convert_to_mp3(video_info['file_path'])
            print(f"🎵 MP3 guardado en: {mp3_file}")
            
            # Pequeña pausa para asegurar que el archivo esté completamente escrito
            import time
            time.sleep(0.5)
            
            # Verificar que el archivo MP3 se creó correctamente
            if not os.path.exists(mp3_file) or os.path.getsize(mp3_file) == 0:
                print("❌ Error: El archivo MP3 no se creó correctamente")
                return mp3_file

            # Preparar campos extra para los tags ID3
            keywords = video_info.get('keywords') or []
            genre_str = ', '.join(keywords[:5]) if keywords else ''
            publish_date = video_info.get('publish_date') or ''
            year_str = publish_date[:4] if publish_date and len(publish_date) >= 4 else ''
            description = video_info.get('description', '')
            comment_str = description[:200] if description else f"Origen: {source}"

            # Descargar y agregar portada si las bibliotecas están disponibles
            if HAS_METADATA and video_info['thumbnail_url']:
                try:
                    print("🖼️ Procesando portada...")
                    thumbnail_filename = os.path.splitext(mp3_file)[0] + "_thumbnail.jpg"
                    
                    if self.download_thumbnail(video_info['thumbnail_url'], thumbnail_filename):
                        if os.path.exists(thumbnail_filename) and os.path.getsize(thumbnail_filename) > 0:
                            print("📸 Portada descargada, añadiendo metadatos...")
                            success = self.add_metadata_to_mp3(
                                mp3_file,
                                video_info['title'],
                                video_info['author'],
                                thumbnail_filename,
                                origin=source,
                                album=video_info.get('author', ''),
                                year=year_str,
                                genre=genre_str,
                                comment=comment_str,
                            )
                            if success:
                                print("✅ Metadatos y portada añadidos correctamente")
                            else:
                                print("⚠️ Metadatos añadidos sin portada")
                            try:
                                os.remove(thumbnail_filename)
                                print("🗑️ Thumbnail temporal eliminada")
                            except:
                                pass
                        else:
                            print("❌ Error: Thumbnail descargada pero vacía o inválida")
                            self.add_metadata_to_mp3(
                                mp3_file, video_info['title'], video_info['author'],
                                origin=source, album=video_info.get('author', ''),
                                year=year_str, genre=genre_str, comment=comment_str,
                            )
                    else:
                        print("❌ No se pudo descargar la portada")
                        self.add_metadata_to_mp3(
                            mp3_file, video_info['title'], video_info['author'],
                            origin=source, album=video_info.get('author', ''),
                            year=year_str, genre=genre_str, comment=comment_str,
                        )
                except Exception as e:
                    print(f"⚠️ Error con metadatos/portada: {e}")
                    print("🎵 El archivo MP3 se creó correctamente sin metadatos")
            else:
                if not HAS_METADATA:
                    print("💡 Tip: Instala 'mutagen' para agregar portadas a tus MP3")
                elif not video_info.get('thumbnail_url'):
                    print("⚠️ No se encontró URL de portada en el video")

            # ── Guardar JSON de metadatos ──────────────────────────────────
            mp3_abs = os.path.normpath(os.path.abspath(mp3_file))
            self._save_metadata_to_json(video_info, mp3_abs)

            # ── Guardar en BD ──────────────────────────────────────────────
            if _DB_ADAPTER_OK:
                try:
                    metadata_bd = {
                        'titulo':           video_info.get('title', ''),
                        'artista':          video_info.get('author', ''),
                        'duracion_seg':     video_info.get('length') or None,
                        'genero':           genre_str or None,
                        'plataforma_origen': 'YouTube',
                        'url_origen':       url,
                        'ruta_local':       mp3_abs,
                        'caratula_url':     video_info.get('thumbnail_url') or None,
                    }
                    id_cancion = upsert_cancion(metadata_bd)
                    registrar_descarga(id_cancion, formato='mp3')
                except Exception as _bd_err:
                    print(f"⚠️ No se pudo guardar en BD: {_bd_err}")
            # ───────────────────────────────────────────────────────────────

            return mp3_file
            
        except Exception as e:
            print(f"❌ Error en el proceso de conversión: {e}")
            raise
