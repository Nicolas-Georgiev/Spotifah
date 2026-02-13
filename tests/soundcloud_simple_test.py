# soundcloud_simple_test.py
"""
Test simple para diagnosticar problemas específicos con SoundCloud
"""

import subprocess
import sys
import os
import json
import datetime
from pathlib import Path

# Intentar importar bibliotecas para metadatos
HAS_METADATA = False
METADATA_TYPE = None

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3
    HAS_METADATA = True
    METADATA_TYPE = "mutagen"
    print("✅ Usando mutagen para leer metadatos")
except ImportError:
    try:
        import eyed3
        HAS_METADATA = True
        METADATA_TYPE = "eyed3"
        print("✅ Usando eyed3 para leer metadatos")
    except ImportError:
        print("⚠️ No hay bibliotecas de metadatos disponibles")
        print("   Instala: pip install mutagen")

def extract_cover_art(file_path, output_dir=None):
    """Extrae la portada del archivo MP3 y la guarda como imagen separada"""
    if not HAS_METADATA:
        print("⚠️ No hay bibliotecas de metadatos disponibles para extraer portada")
        return None
    
    if output_dir is None:
        # Usar carpeta assets/covers por defecto
        output_dir = Path("assets/covers")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        if METADATA_TYPE == "mutagen":
            audio = MP3(file_path, ID3=ID3)
            
            if audio.tags:
                for key in audio.tags.keys():
                    if key.startswith('APIC'):
                        apic = audio.tags[key]
                        
                        # Determinar extensión de archivo según MIME type
                        if apic.mime == 'image/jpeg':
                            ext = '.jpg'
                        elif apic.mime == 'image/png':
                            ext = '.png'
                        elif apic.mime == 'image/gif':
                            ext = '.gif'
                        else:
                            ext = '.jpg'  # Default
                        
                        # Crear nombre de archivo para la portada
                        base_name = file_path.stem
                        cover_filename = f"{base_name}_cover{ext}"
                        cover_path = output_dir / cover_filename
                        
                        # Guardar imagen
                        with open(cover_path, 'wb') as f:
                            f.write(apic.data)
                        
                        print(f"🖼️ Portada extraída: {cover_path}")
                        print(f"   📄 Formato: {apic.mime}")
                        print(f"   📏 Tamaño: {len(apic.data)} bytes")
                        print(f"   📐 Tipo: {apic.type} ({'Portada frontal' if apic.type == 3 else 'Otra'})")
                        
                        return {
                            "archivo_portada": str(cover_path),
                            "formato": apic.mime,
                            "tamaño_bytes": len(apic.data),
                            "tipo": apic.type,
                            "extraida_exitosamente": True
                        }
        
        elif METADATA_TYPE == "eyed3":
            import eyed3
            audiofile = eyed3.load(file_path)
            
            if audiofile.tag and audiofile.tag.images:
                for i, image in enumerate(audiofile.tag.images):
                    # Determinar extensión
                    if image.mime_type == 'image/jpeg':
                        ext = '.jpg'
                    elif image.mime_type == 'image/png':
                        ext = '.png'
                    else:
                        ext = '.jpg'
                    
                    # Nombre de archivo
                    base_name = file_path.stem
                    cover_filename = f"{base_name}_cover{f'_{i+1}' if len(audiofile.tag.images) > 1 else ''}{ext}"
                    cover_path = output_dir / cover_filename
                    
                    # Guardar imagen
                    with open(cover_path, 'wb') as f:
                        f.write(image.image_data)
                    
                    print(f"🖼️ Portada {i+1} extraída: {cover_path}")
                    print(f"   📄 Formato: {image.mime_type}")
                    print(f"   📏 Tamaño: {len(image.image_data)} bytes")
                    
                    # Retornar info de la primera imagen
                    if i == 0:
                        return {
                            "archivo_portada": str(cover_path),
                            "formato": image.mime_type,
                            "tamaño_bytes": len(image.image_data),
                            "extraida_exitosamente": True
                        }
        
        print("⚠️ No se encontró portada en el archivo")
        return {"extraida_exitosamente": False, "razon": "No se encontró portada"}
        
    except Exception as e:
        print(f"❌ Error al extraer portada: {e}")
        return {"extraida_exitosamente": False, "razon": str(e)}

def read_metadata(file_path, extract_cover=True):
    """Lee y muestra los metadatos de un archivo MP3"""
    print(f"\n📋 Leyendo metadatos de: {file_path.name}")
    
    if not HAS_METADATA:
        print("⚠️ No hay bibliotecas de metadatos disponibles")
        return None
    
    metadata = {
        "archivo": str(file_path),
        "nombre": file_path.name,
        "tamaño_bytes": file_path.stat().st_size,
        "tamaño_mb": round(file_path.stat().st_size / (1024*1024), 2),
        "fecha_analisis": datetime.datetime.now().isoformat(),
        "metadatos": {}
    }
    
    try:
        if METADATA_TYPE == "mutagen":
            audio = MP3(file_path, ID3=ID3)
            
            # Metadatos básicos
            metadata["metadatos"]["titulo"] = str(audio.get('TIT2', ['No disponible'])[0]) if audio.get('TIT2') else 'No disponible'
            metadata["metadatos"]["artista"] = str(audio.get('TPE1', ['No disponible'])[0]) if audio.get('TPE1') else 'No disponible'
            metadata["metadatos"]["album"] = str(audio.get('TALB', ['No disponible'])[0]) if audio.get('TALB') else 'No disponible'
            metadata["metadatos"]["año"] = str(audio.get('TDRC', ['No disponible'])[0]) if audio.get('TDRC') else 'No disponible'
            metadata["metadatos"]["genero"] = str(audio.get('TCON', ['No disponible'])[0]) if audio.get('TCON') else 'No disponible'
            metadata["metadatos"]["comentario"] = str(audio.get('COMM::eng', ['No disponible'])[0]) if audio.get('COMM::eng') else 'No disponible'
            
            # Información técnica
            if audio.info:
                metadata["metadatos"]["duracion_segundos"] = round(audio.info.length, 2)
                metadata["metadatos"]["duracion_formato"] = f"{int(audio.info.length//60)}:{int(audio.info.length%60):02d}"
                metadata["metadatos"]["bitrate"] = audio.info.bitrate
                metadata["metadatos"]["canales"] = audio.info.channels
                metadata["metadatos"]["tipo_canales"] = "Estéreo" if audio.info.channels == 2 else "Mono" if audio.info.channels == 1 else "Multi-canal"
                metadata["metadatos"]["frecuencia_muestreo"] = audio.info.sample_rate
            
            # Verificar portada
            metadata["metadatos"]["tiene_portada"] = False
            metadata["metadatos"]["portada_info"] = {}
            
            if audio.tags:
                for key in audio.tags.keys():
                    if key.startswith('APIC'):
                        apic = audio.tags[key]
                        metadata["metadatos"]["tiene_portada"] = True
                        metadata["metadatos"]["portada_info"] = {
                            "tipo": apic.type,
                            "tipo_descripcion": "Portada frontal" if apic.type == 3 else "Otra",
                            "formato": apic.mime,
                            "tamaño_bytes": len(apic.data)
                        }
                        break
                
                # Todos los tags (sin datos binarios)
                metadata["metadatos"]["todos_los_tags"] = {}
                for key, value in audio.tags.items():
                    if not key.startswith('APIC'):
                        try:
                            metadata["metadatos"]["todos_los_tags"][key] = str(value)
                        except:
                            metadata["metadatos"]["todos_los_tags"][key] = "Error al convertir"
            
            print("🎵 Metadatos encontrados:")
            print(f"   📝 Título: {metadata['metadatos']['titulo']}")
            print(f"   👤 Artista: {metadata['metadatos']['artista']}")
            print(f"   💿 Álbum: {metadata['metadatos']['album']}")
            print(f"   🕐 Duración: {metadata['metadatos']['duracion_formato']}")
            print(f"   🎧 Bitrate: {metadata['metadatos']['bitrate']} kbps")
            print(f"   📊 Canales: {metadata['metadatos']['tipo_canales']}")
            print(f"   🔊 Frecuencia: {metadata['metadatos']['frecuencia_muestreo']} Hz")
            
            if metadata["metadatos"]["tiene_portada"]:
                print("   🖼️ Portada: ✅ Presente")
                
                # Extraer portada como archivo separado si se solicita
                if extract_cover:
                    cover_info = extract_cover_art(file_path)
                    if cover_info and cover_info.get("extraida_exitosamente"):
                        metadata["metadatos"]["portada_extraida"] = cover_info
            else:
                print("   🖼️ Portada: ❌ No presente")
        
        elif METADATA_TYPE == "eyed3":
            import eyed3
            audiofile = eyed3.load(file_path)
            
            if audiofile.tag:
                metadata["metadatos"]["titulo"] = audiofile.tag.title or 'No disponible'
                metadata["metadatos"]["artista"] = audiofile.tag.artist or 'No disponible'
                metadata["metadatos"]["album"] = audiofile.tag.album or 'No disponible'
                metadata["metadatos"]["año"] = str(audiofile.tag.recording_date) if audiofile.tag.recording_date else 'No disponible'
                metadata["metadatos"]["genero"] = audiofile.tag.genre.name if audiofile.tag.genre else 'No disponible'
                
                if audiofile.info:
                    metadata["metadatos"]["duracion_segundos"] = round(audiofile.info.time_secs, 2)
                    metadata["metadatos"]["duracion_formato"] = f"{int(audiofile.info.time_secs//60)}:{int(audiofile.info.time_secs%60):02d}"
                    metadata["metadatos"]["bitrate"] = audiofile.info.bit_rate[1]
                
                # Portadas
                metadata["metadatos"]["tiene_portada"] = bool(audiofile.tag.images)
                if audiofile.tag.images:
                    metadata["metadatos"]["portada_info"] = {
                        "cantidad": len(audiofile.tag.images),
                        "formato": audiofile.tag.images[0].mime_type,
                        "tamaño_bytes": len(audiofile.tag.images[0].image_data)
                    }
                
                print("🎵 Metadatos encontrados:")
                print(f"   📝 Título: {metadata['metadatos']['titulo']}")
                print(f"   👤 Artista: {metadata['metadatos']['artista']}")
                print(f"   💿 Álbum: {metadata['metadatos']['album']}")
                if 'duracion_formato' in metadata["metadatos"]:
                    print(f"   🕐 Duración: {metadata['metadatos']['duracion_formato']}")
                if metadata["metadatos"]["tiene_portada"]:
                    print("   🖼️ Portada: ✅ Presente")
                    
                    # Extraer portada como archivo separado si se solicita
                    if extract_cover:
                        cover_info = extract_cover_art(file_path)
                        if cover_info and cover_info.get("extraida_exitosamente"):
                            metadata["metadatos"]["portada_extraida"] = cover_info
                else:
                    print("   🖼️ Portada: ❌ No presente")
            else:
                print("⚠️ No se encontraron metadatos en el archivo")
                metadata["metadatos"]["error"] = "No se encontraron metadatos"
                
    except Exception as e:
        print(f"❌ Error al leer metadatos: {e}")
        metadata["metadatos"]["error"] = str(e)
    
    return metadata

def save_metadata_to_json(metadata_list, output_file="metadata_soundcloud.json"):
    """Guarda la lista de metadatos en un archivo JSON"""
    try:
        # Crear estructura del JSON
        json_data = {
            "fecha_generacion": datetime.datetime.now().isoformat(),
            "total_archivos": len(metadata_list),
            "herramienta": "SoundCloud Simple Test",
            "version": "1.0",
            "archivos": metadata_list
        }
        
        # Guardar archivo JSON
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Metadatos guardados en: {output_path}")
        print(f"📊 Total de archivos analizados: {len(metadata_list)}")
        return True
        
    except Exception as e:
        print(f"❌ Error al guardar JSON: {e}")
        return False

def test_scdl_basic():
    """Test básico de scdl"""
    print("🧪 Test básico de scdl...")
    
    url = "https://soundcloud.com/fakemink/ragebait-prod-deer-park"
    output_dir = Path("data/music")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_list = []
    
    try:
        print(f"📥 Intentando descargar: {url}")
        print("⏳ Esto puede tardar un momento...")
        
        # Comando scdl básico con parámetros correctos
        cmd = [
            "scdl", 
            "-l", url,
            "--path", str(output_dir),
            "--onlymp3",
            "--original-art",
            "--extract-artist"
        ]
        
        print(f"🔧 Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"\n📊 Código de salida: {result.returncode}")
        
        if result.stdout:
            print(f"📤 Salida estándar:")
            print(result.stdout)
        
        if result.stderr:
            print(f"⚠️ Errores:")
            print(result.stderr)
        
        # Verificar archivos descargados
        mp3_files = list(output_dir.glob("*.mp3"))
        if mp3_files:
            print(f"✅ Archivos descargados: {len(mp3_files)}")
            for file in mp3_files:
                print(f"   📁 {file.name} ({file.stat().st_size} bytes)")
                # Leer metadatos de cada archivo descargado con scdl
                metadata = read_metadata(file)
                if metadata:
                    metadata_list.append(metadata)
            
            # Guardar metadatos en JSON solo si se especifica
            # if metadata_list:
            #     save_metadata_to_json(metadata_list, f"metadata_scdl_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            return True
        else:
            print("❌ No se descargaron archivos MP3")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - La descarga tardó más de 2 minutos")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ytdlp_basic():
    """Test básico de yt-dlp"""
    print("\n🧪 Test básico de yt-dlp...")
    
    url = "https://soundcloud.com/fakemink/ragebait-prod-deer-park"
    output_dir = Path("data/music")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    metadata_list = []
    
    try:
        print(f"📥 Intentando descargar con yt-dlp: {url}")
        
        # Comando yt-dlp básico
        cmd = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(output_dir / "%(title)s.%(ext)s"),
            "--verbose",
            url
        ]
        
        print(f"🔧 Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"\n📊 Código de salida: {result.returncode}")
        
        if result.stdout:
            print(f"📤 Salida estándar:")
            print(result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout)
        
        if result.stderr:
            print(f"⚠️ Errores:")
            print(result.stderr[:1000] + "..." if len(result.stderr) > 1000 else result.stderr)
        
        # Verificar archivos descargados
        mp3_files = list(output_dir.glob("*.mp3"))
        if mp3_files:
            print(f"✅ Archivos descargados: {len(mp3_files)}")
            for file in mp3_files:
                print(f"   📁 {file.name} ({file.stat().st_size} bytes)")
                # Leer metadatos de cada archivo descargado con yt-dlp
                metadata = read_metadata(file)
                if metadata:
                    metadata_list.append(metadata)
            
            # Guardar metadatos en JSON solo si se especifica
            # if metadata_list:
            #     save_metadata_to_json(metadata_list, f"metadata_ytdlp_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            return True
        else:
            print("❌ No se descargaron archivos MP3")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - La descarga tardó más de 2 minutos")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    """Test básico de scdl"""
    print("🧪 Test básico de scdl...")
    
    url = "https://soundcloud.com/fakemink/ragebait-prod-deer-park"
    output_dir = Path("test_downloads")
    output_dir.mkdir(exist_ok=True)
    
    try:
        print(f"📥 Intentando descargar: {url}")
        print("⏳ Esto puede tardar un momento...")
        
        # Comando scdl básico con parámetros correctos
        cmd = [
            "scdl", 
            "-l", url,
            "--path", str(output_dir),
            "--onlymp3",
            "--original-art",
            "--extract-artist"
        ]
        
        print(f"🔧 Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"\n📊 Código de salida: {result.returncode}")
        
        if result.stdout:
            print(f"📤 Salida estándar:")
            print(result.stdout)
        
        if result.stderr:
            print(f"⚠️ Errores:")
            print(result.stderr)
        
        # Verificar archivos descargados
        mp3_files = list(output_dir.glob("*.mp3"))
        if mp3_files:
            print(f"✅ Archivos descargados: {len(mp3_files)}")
            for file in mp3_files:
                print(f"   📁 {file.name} ({file.stat().st_size} bytes)")
                # Leer metadatos de cada archivo descargado con scdl
                read_metadata(file)
            return True
        else:
            print("❌ No se descargaron archivos MP3")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - La descarga tardó más de 2 minutos")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ytdlp_basic():
    """Test básico de yt-dlp"""
    print("\n🧪 Test básico de yt-dlp...")
    
    url = "https://soundcloud.com/fakemink/ragebait-prod-deer-park"
    output_dir = Path("test_downloads_ytdlp")
    output_dir.mkdir(exist_ok=True)
    
    try:
        print(f"📥 Intentando descargar con yt-dlp: {url}")
        
        # Comando yt-dlp básico
        cmd = [
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(output_dir / "%(title)s.%(ext)s"),
            "--verbose",
            url
        ]
        
        print(f"🔧 Comando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"\n📊 Código de salida: {result.returncode}")
        
        if result.stdout:
            print(f"📤 Salida estándar:")
            print(result.stdout[:1000] + "..." if len(result.stdout) > 1000 else result.stdout)
        
        if result.stderr:
            print(f"⚠️ Errores:")
            print(result.stderr[:1000] + "..." if len(result.stderr) > 1000 else result.stderr)
        
        # Verificar archivos descargados
        mp3_files = list(output_dir.glob("*.mp3"))
        if mp3_files:
            print(f"✅ Archivos descargados: {len(mp3_files)}")
            for file in mp3_files:
                print(f"   📁 {file.name} ({file.stat().st_size} bytes)")
                # Leer metadatos de cada archivo descargado con yt-dlp
                read_metadata(file)
            return True
        else:
            print("❌ No se descargaron archivos MP3")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - La descarga tardó más de 2 minutos")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_url_info():
    """Test para extraer información de la URL"""
    print("\n🧪 Test de extracción de información...")
    
    url = "https://soundcloud.com/fakemink/ragebait-prod-deer-park"
    
    try:
        print(f"📊 Extrayendo info de: {url}")
        
        cmd = ["yt-dlp", "--dump-json", "--no-download", url]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"📊 Código de salida: {result.returncode}")
        
        if result.returncode == 0 and result.stdout:
            import json
            info = json.loads(result.stdout)
            print(f"✅ Información extraída:")
            print(f"   🎵 Título: {info.get('title', 'No disponible')}")
            print(f"   👤 Artista: {info.get('uploader', 'No disponible')}")
            print(f"   ⏱️ Duración: {info.get('duration', 'No disponible')} segundos")
            print(f"   🔗 URL: {info.get('webpage_url', 'No disponible')}")
            return True
        else:
            print(f"❌ Error al extraer información")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout al extraer información")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🎵 SoundCloud Simple Test")
    print("=" * 50)
    
    # Test 1: Información de la URL
    info_ok = test_url_info()
    
    if info_ok:
        print("\n" + "="*50)
        
        # Test 2: Descarga con scdl
        scdl_ok = test_scdl_basic()
        
        if not scdl_ok:
            print("\n" + "="*50)
            # Test 3: Descarga con yt-dlp como fallback
            ytdlp_ok = test_ytdlp_basic()
            
            if ytdlp_ok:
                print("\n✅ yt-dlp funciona como alternativa")
            else:
                print("\n❌ Ningún método de descarga funciona")
        else:
            print("\n✅ scdl funciona correctamente")
    else:
        print("\n❌ No se puede extraer información de la URL")
        print("💡 Verifica que la URL sea válida y esté disponible")
    
    print("\n🏁 Test completado")