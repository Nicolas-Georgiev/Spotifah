# spotify2mp3_model.py
import os
import sys
import re
import json
import requests
import tempfile
import datetime
from model.conversor_model import BaseModel

# Adaptador de BD — importación segura para no bloquear si la BD no está disponible
try:
    from model.db_adapter import upsert_cancion, registrar_descarga
    _DB_ADAPTER_OK = True
except Exception as _db_e:
    print(f"⚠️ spotify2mp3_model: db_adapter no disponible ({_db_e})")
    _DB_ADAPTER_OK = False

# Bibliotecas esenciales simplificadas
try:
    from moviepy.editor import AudioFileClip
    print("✅ Usando moviepy para conversión de audio de Spotify")
except ImportError:
    print("⚠️ moviepy no disponible. Instala: pip install moviepy")
    raise ImportError("moviepy es requerido para conversión")

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB # type: ignore
    print("✅ Usando mutagen para metadatos de audio de Spotify")
except ImportError:
    print("⚠️ mutagen no disponible. Instala: pip install mutagen")
    raise ImportError("mutagen es requerido para metadatos")

# Bibliotecas obligatorias
try:
    import yt_dlp
    print("✅ Usando yt-dlp para descargas desde YouTube")
except ImportError:
    print("⚠️ yt-dlp no disponible. Instala: pip install yt-dlp")
    raise ImportError("yt-dlp es requerido para descargas")

try:
    from spotdl.search.song_gatherer import from_spotify_url as spotdl_from_spotify_url
    SPOTDL_API_MODE = "song_gatherer"
    print("✅ Usando spotdl.search.song_gatherer para metadatos de Spotify")
except ImportError:
    try:
        from spotdl import Spotdl
        from spotdl.utils.config import get_config
        SPOTDL_API_MODE = "legacy_spotdl_class"
        print("✅ Usando API legacy de spotdl para metadatos de Spotify")
    except ImportError:
        print("🚨 ERROR: spotdl no disponible - ES OBLIGATORIO")
        print("   📦 INSTALAR: pip install spotdl")
        raise ImportError("spotdl es requerido para el funcionamiento")

# Singleton de SpotifyInfoExtractor — spotdl usa SpotifyClient global internamente,
# por lo que crear múltiples instancias de Spotdl() causa conflictos.
# Compartir una única instancia permite tener varios Spotify2MP3Converter simultáneos.
_SHARED_INFO_EXTRACTOR: 'SpotifyInfoExtractor | None' = None
_EXTRACTOR_LOCK = __import__('threading').Lock()


def _get_shared_extractor() -> 'SpotifyInfoExtractor':
    """Devuelve (o crea) el SpotifyInfoExtractor compartido (thread-safe)."""
    global _SHARED_INFO_EXTRACTOR
    if _SHARED_INFO_EXTRACTOR is None:
        with _EXTRACTOR_LOCK:
            if _SHARED_INFO_EXTRACTOR is None:
                _SHARED_INFO_EXTRACTOR = SpotifyInfoExtractor()
    return _SHARED_INFO_EXTRACTOR


class SpotifyInfoExtractor:
    """Extrae información de Spotify usando spotdl como método principal y métodos alternativos como fallback"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Configurar spotdl (OBLIGATORIO)
        try:
            if SPOTDL_API_MODE == "legacy_spotdl_class":
                # Compatibilidad con versiones antiguas de SpotDL
                # Priorizar variables de entorno, luego .env, finalmente la configuración interna de spotdl
                client_id = os.getenv('SPOTDL_CLIENT_ID') or os.getenv('SPOTIFY_CLIENT_ID') or os.getenv('CLIENT_ID')
                client_secret = os.getenv('SPOTDL_CLIENT_SECRET') or os.getenv('SPOTIFY_CLIENT_SECRET') or os.getenv('CLIENT_SECRET')

                # Intentar cargar desde .env en la raíz del proyecto si no están en el entorno
                if not client_id or not client_secret:
                    try:
                        try:
                            from frozen_utils import get_dotenv_path
                            dotenv_path = get_dotenv_path()
                        except ImportError:
                            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                            dotenv_path = os.path.join(project_root, '.env')
                        if os.path.exists(dotenv_path):
                            with open(dotenv_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    line = line.strip()
                                    if not line or line.startswith('#') or '=' not in line:
                                        continue
                                    k, v = line.split('=', 1)
                                    k = k.strip()
                                    v = v.strip().strip('"').strip("'")
                                    if k in ('SPOTDL_CLIENT_ID', 'SPOTDL_CLIENT_SECRET', 'SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'CLIENT_ID', 'CLIENT_SECRET'):
                                        if 'CLIENT_ID' in k and not client_id:
                                            client_id = v
                                        if 'CLIENT_SECRET' in k and not client_secret:
                                            client_secret = v
                    except Exception:
                        # No bloquear si falla la lectura del .env
                        pass

                # Finalmente intentar obtener configuración interna de spotdl si aún faltan
                if not client_id or not client_secret:
                    try:
                        config = get_config() # type: ignore
                        if not client_id:
                            client_id = config.get('client_id')
                        if not client_secret:
                            client_secret = config.get('client_secret')
                    except Exception:
                        # dejar como None si no hay config
                        pass

                if client_id and client_secret:
                    self.spotdl = Spotdl(
                        client_id=client_id,
                        client_secret=client_secret,
                        downloader_settings={"ffmpeg": self._get_ffmpeg_path()},
                    )
                else:
                    self.spotdl = Spotdl(
                        downloader_settings={"ffmpeg": self._get_ffmpeg_path()},
                    )
            else:
                self.spotdl = None

            print("✅ SpotDL configurado exitosamente")
            
        except Exception as e:
            print(f"🚨 Error configurando SpotDL: {e}")
            raise RuntimeError("SpotDL es obligatorio para el funcionamiento")

    @staticmethod
    def _get_ffmpeg_path() -> str:
        ffmpeg = os.environ.get('EKHO_FFMPEG_PATH')
        if ffmpeg:
            return ffmpeg
        if getattr(sys, 'frozen', False):
            bundled = os.path.join(
                sys._MEIPASS,
                'imageio_ffmpeg', 'binaries',
                'ffmpeg-win-x86_64-v7.1.exe'
            )
            if os.path.exists(bundled):
                return bundled
        return 'ffmpeg'

    def get_track_info(self, spotify_url: str):
        """Obtiene información de una pista usando SpotDL y métodos alternativos como fallback"""
        track_id = self._extract_spotify_id(spotify_url)
        if not track_id:
            return None

        # 1. Intentar con SpotDL
        track_info = self._get_info_from_spotdl(spotify_url)
        if track_info and track_info.get('artista') != 'Artista Desconocido':
            print("✅ Metadatos obtenidos via SpotDL")
            return track_info

        print("⚠️ SpotDL falló, intentando métodos alternativos...")

        # 2. Intentar extraer de la página principal de Spotify
        track_info = self._get_info_from_main_page(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via página principal")
            return self._normalize_fallback_info(track_info, spotify_url)

        # 3. Intentar con OEmbed
        track_info = self._get_info_from_oembed(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via OEmbed")
            return self._normalize_fallback_info(track_info, spotify_url)

        # 4. Intentar con página embed
        track_info = self._get_info_from_embed(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via embed")
            return self._normalize_fallback_info(track_info, spotify_url)

        # 5. Intentar con APIs alternativas (iTunes, etc.)
        track_info = self._search_alternative_apis(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via APIs alternativas")
            return self._normalize_fallback_info(track_info, spotify_url)

        raise RuntimeError(
            f"No se pudieron obtener metadatos para: {spotify_url}. "
            f"Verifica que la URL sea válida y que las credenciales de Spotify estén configuradas."
        )

    def _normalize_fallback_info(self, raw: dict, spotify_url: str) -> dict:
        """Normaliza la información obtenida de métodos fallback al formato canónico"""
        name = raw.get('name', raw.get('titulo', 'Título Desconocido'))
        artist = raw.get('artist', raw.get('artista', 'Artista Desconocido'))
        image = raw.get('image_url', raw.get('caratula_url', ''))
        album = raw.get('album', 'Álbum Desconocido')
        duration = raw.get('duration', raw.get('duracion_seg', 180))

        return {
            'titulo':           name,
            'artista':          artist,
            'caratula_url':     image,
            'duracion_seg':     int(duration),
            'genero':           '',
            'plataforma_origen': 'Spotify',
            'url_origen':       spotify_url,
            'ruta_local':       '',
            'letra':            '',
            'album':            album,
            'name':             name,
            'artist':           artist,
            'artists':          [artist],
            'duration_ms':      int(duration) * 1000,
            'images':           [{'url': image}] if image else [],
            'image_url':        image,
        }

    def _get_info_from_spotdl(self, spotify_url: str):
        """Método PRINCIPAL: Extraer información usando SpotDL"""
        try:
            # Resolver metadatos con API de SpotDL compatible con múltiples versiones
            if SPOTDL_API_MODE == "song_gatherer":
                song = spotdl_from_spotify_url(spotify_url) # type: ignore
                if song is None:
                    print("⚠️ SpotDL: No se encontraron resultados")
                    return None
            else:
                songs = self.spotdl.search([spotify_url]) # type: ignore
                if not songs or len(songs) == 0:
                    print("⚠️ SpotDL: No se encontraron resultados")
                    return None
                song = songs[0]

            song_name = getattr(song, 'name', None) or getattr(song, 'song_name', None)
            song_artists = getattr(song, 'artists', None) or getattr(song, 'contributing_artists', None) or []
            song_cover_url = getattr(song, 'cover_url', None) or getattr(song, 'album_cover_url', None) or ''
            song_album_name = getattr(song, 'album_name', None)
            song_duration = getattr(song, 'duration', None)
            song_genres = getattr(song, 'genres', None) or []
            song_isrc = getattr(song, 'isrc', None) or ''
            song_release_date = getattr(song, 'date', None) or getattr(song, 'album_release', None) or ''
            lyrics = (getattr(song, 'lyrics', None) or '').strip()

            if isinstance(song_artists, str):
                artists_value = song_artists
            else:
                artists_value = ', '.join(song_artists) if song_artists else 'Artista Desconocido'
            
            # Extraer metadatos completos
            track_info = {
                'titulo': song_name or 'Título Desconocido',
                'artista': artists_value,
                'album': song_album_name or 'Álbum Desconocido',
                'duracion_seg': int(song_duration or 180),
                'genero': ', '.join(song_genres) if song_genres else 'Género Desconocido',
                'plataforma_origen': 'Spotify',
                'url_origen': spotify_url,
                'ruta_local': '',  # Se llenará cuando se descargue
                'caratula_url': song_cover_url,
                'letra': lyrics.strip() if lyrics else 'Letra no disponible',
                # Campos adicionales para compatibilidad
                'name': song_name or 'Unknown Title',
                'artist': artists_value if artists_value else 'Unknown Artist',
                'image_url': song_cover_url,
                'duration': int(song_duration or 180),
                'track_id': self._extract_spotify_id(spotify_url),
                'isrc': song_isrc,
                'release_date': str(song_release_date) if song_release_date else '',
                'genres': song_genres
            }
            
            # Validar que tenemos información útil
            if (track_info['titulo'] != 'Título Desconocido' and 
                track_info['artista'] != 'Artista Desconocido' and
                len(track_info['artista']) > 1):
                return track_info
            else:
                print("⚠️ SpotDL: Metadatos incompletos")
                return None
                
        except Exception as e:
            print(f"⚠️ Error en SpotDL: {e}")
            return None
            


    @staticmethod
    def _extract_spotify_id(url: str):
        """Extrae el ID de Spotify de la URL"""
        patterns = [
            r"https://open\.spotify\.com/(?:intl-\w+/)?track/([a-zA-Z0-9]+)",
            r"spotify:track:([a-zA-Z0-9]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _get_info_from_main_page(self, track_id: str):
        """Método 1: Extraer información de la página principal de Spotify"""
        try:
            main_url = f"https://open.spotify.com/track/{track_id}"
            response = self.session.get(main_url, timeout=15) # type: ignore
            
            if response.status_code == 200:
                html = response.text
                
                # Método 1: Buscar en el título de la página
                title_pattern = r'<title>([^<]+)</title>'
                title_match = re.search(title_pattern, html, re.IGNORECASE)
                
                if title_match:
                    page_title = title_match.group(1).strip()
                    # Formato típico: "Song - song by Artist | Spotify"
                    page_title = re.sub(r'\s*\|\s*Spotify.*$', '', page_title)
                    
                    # Diferentes patrones de título
                    patterns_to_try = [
                        r'^(.+?)\s*-\s*song\s+(?:and\s+lyrics\s+)?by\s+(.+?)$',  # "Song - song and lyrics by Artist"
                        r'^(.+?)\s*-\s*song\s+(?:and\s+lyrics\s+)?(?:by\s+)?(.+?)$',  # "Song - song and lyrics Artist"
                        r'^(.+?)\s+by\s+(.+?)$',                                # "Song by Artist"
                        r'^(.+?)\s*·\s*(.+?)$',                                 # "Song · Artist"
                        r'^(.+?)\s*-\s*(.+?)$',                                 # "Song - Artist"
                    ]
                    
                    for pattern in patterns_to_try:
                        match = re.search(pattern, page_title, re.IGNORECASE)
                        if match:
                            song = match.group(1).strip()
                            artist = match.group(2).strip()
                            
                            # Limpiar el nombre de la canción
                            song = re.sub(r'\s*-\s*(?:song|music|audio)(?:\s+and\s+lyrics)?.*$', '', song, flags=re.IGNORECASE)
                            song = re.sub(r'\s*\(\s*(?:official|audio|music|video).*?\)\s*', '', song, flags=re.IGNORECASE)
                            
                            # Limpiar el artista
                            artist = re.sub(r'\s*-\s*(?:song|music|audio)(?:\s+and\s+lyrics)?.*$', '', artist, flags=re.IGNORECASE)
                            
                            # Validaciones básicas
                            if (len(song) > 0 and len(artist) > 1 and 
                                not artist.isdigit() and 
                                artist.lower() not in ['song', 'music', 'audio', 'lyrics']):
                                
                                # Buscar álbum en el HTML
                                album = self._extract_album_from_html(html)
                                
                                # Buscar imagen
                                image_url = self._extract_image_from_html(html)
                                
                                return {
                                    'name': song,
                                    'artist': artist,
                                    'album': album,
                                    'image_url': image_url,
                                    'duration': 180,
                                    'track_id': track_id
                                }
                
                # Método 2: Buscar meta tags como fallback
                meta_patterns = {
                    'title': r'<meta\s+property="og:title"\s+content="([^"]+)"',
                    'description': r'<meta\s+property="og:description"\s+content="([^"]+)"',
                    'image': r'<meta\s+property="og:image"\s+content="([^"]+)"',
                }
                
                extracted = {}
                for key, pattern in meta_patterns.items():
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        extracted[key] = match.group(1)
                
                if extracted.get('title'):
                    title = extracted['title']
                    description = extracted.get('description', '')
                    
                    # Intentar extraer información del meta título
                    if ' · ' in title:
                        parts = title.split(' · ')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            potential_artist = parts[1].strip()
                            if not potential_artist.isdigit() and len(potential_artist) > 1:
                                album = self._extract_album_from_html(html)
                                return {
                                    'name': name,
                                    'artist': potential_artist,
                                    'album': album,
                                    'image_url': extracted.get('image', ''),
                                    'duration': 180,
                                    'track_id': track_id
                                }
                    
                    # Buscar en descripción
                    if description:
                        desc_patterns = [
                            r'Listen to (.+?) (?:by|from) (.+?) on Spotify',
                            r'Escucha (.+?) de (.+?) en Spotify',
                            r'(.+?) · Song · (.+?) · \d+',
                        ]
                        
                        for desc_pattern in desc_patterns:
                            desc_match = re.search(desc_pattern, description)
                            if desc_match and len(desc_match.groups()) >= 2:
                                song = desc_match.group(1).strip()
                                artist = desc_match.group(2).strip()
                                if not artist.isdigit() and len(artist) > 1:
                                    album = self._extract_album_from_html(html)
                                    return {
                                        'name': song,
                                        'artist': artist,
                                        'album': album,
                                        'image_url': extracted.get('image', ''),
                                        'duration': 180,
                                        'track_id': track_id
                                    }
                
        except Exception as e:
            print(f"⚠️ Página principal falló: {e}")
        return None
    
    @staticmethod
    def _extract_album_from_html(html):
        """Extrae información del álbum del HTML"""
        album_patterns = [
            r'"album"[^}]*?"name"\s*:\s*"([^"]+)"',
            r'"albumName"\s*:\s*"([^"]+)"',
            r'data-testid="album"[^>]*>([^<]+)<',
            r'album.*?name.*?"([^"]+)"',
            r'<meta\s+property="music:album"\s+content="([^"]+)"',
            r'"collection_name"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in album_patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                album = match.group(1).strip()
                if (album and not album.isdigit() and len(album) > 1 and 
                    album.lower() not in ['track', 'single', 'music:album:track']):
                    return album
        return 'Unknown Album'
    
    @staticmethod
    def _extract_image_from_html(html):
        """Extrae URL de imagen del HTML"""
        image_patterns = [
            r'<meta\s+property="og:image"\s+content="([^"]+)"',
            r'"image"[^}]*?"url"\s*:\s*"([^"]+)"',
            r'"cover"[^}]*?"url"\s*:\s*"([^"]+)"',
        ]
        
        for pattern in image_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return match.group(1)
        return ''

    def _get_info_from_oembed(self, track_id: str):
        """Método 2: Usar endpoint OEmbed público de Spotify"""
        try:
            oembed_url = f"https://open.spotify.com/oembed?url=https://open.spotify.com/track/{track_id}"
            response = self.session.get(oembed_url, timeout=10) # type: ignore
            
            if response.status_code == 200:
                data = response.json()
                title = data.get('title', '')
                
                if title:
                    # Limpiar el título
                    title = title.replace(' on Spotify', '').strip()
                    
                    # Formato OEmbed común: "Song by Artist"
                    if ' by ' in title:
                        parts = title.split(' by ', 1)
                        song_name = parts[0].strip()
                        artist_name = parts[1].strip()
                        
                        # Validar que el artista no sea solo un número o muy corto
                        if len(artist_name) > 2 and not artist_name.isdigit():
                            return {
                                'name': song_name,
                                'artist': artist_name,
                                'album': 'Unknown Album',
                                'image_url': data.get('thumbnail_url', ''),
                                'duration': 180,
                                'track_id': track_id
                            }
                    
                    # Solo devolver el nombre de la canción si no podemos extraer artista
                    return {
                        'name': title,
                        'artist': 'Unknown Artist',
                        'album': 'Unknown Album',
                        'image_url': data.get('thumbnail_url', ''),
                        'duration': 180,
                        'track_id': track_id
                    }
        except Exception as e:
            print(f"⚠️ OEmbed falló: {e}")
        return None

    def _get_info_from_embed(self, track_id: str):
        """Método 2: Extraer de página embed de Spotify"""
        try:
            embed_url = f"https://open.spotify.com/embed/track/{track_id}"
            response = self.session.get(embed_url, timeout=10) # type: ignore
            
            if response.status_code == 200:
                html = response.text
                
                # Buscar JSON embebido
                json_pattern = r'<script[^>]*type=["\']application/json["\'][^>]*>([^<]+)</script>'
                matches = re.finditer(json_pattern, html, re.DOTALL)
                
                for match in matches:
                    try:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                        track_info = self._extract_from_json_recursive(data)
                        if track_info and track_info.get('name'):
                            track_info['track_id'] = track_id
                            return track_info
                    except json.JSONDecodeError:
                        continue
                
                # Fallback: meta tags
                return self._parse_meta_tags(html, track_id)
        except Exception:
            pass
        return None

    def _extract_from_json_recursive(self, data, depth=0):
        """Busca información de track recursivamente en JSON"""
        if depth > 8:
            return None
            
        try:
            if isinstance(data, dict):
                if 'name' in data and ('artist' in data or 'artists' in data):
                    result = {'name': data.get('name', '')}
                    
                    if 'artists' in data and isinstance(data['artists'], list):
                        artists = [artist.get('name', '') if isinstance(artist, dict) else str(artist) 
                                 for artist in data['artists']]
                        result['artist'] = ', '.join(filter(None, artists))
                    elif 'artist' in data:
                        result['artist'] = data['artist'].get('name', '') if isinstance(data['artist'], dict) else str(data['artist'])
                    
                    if 'album' in data and isinstance(data['album'], dict):
                        result['album'] = data['album'].get('name', 'Unknown Album')
                        if 'images' in data['album'] and data['album']['images']:
                            result['image_url'] = data['album']['images'][0].get('url', '')
                    
                    if 'duration_ms' in data:
                        result['duration'] = int(data['duration_ms']) // 1000
                    
                    return result if result['name'] else None
                
                for key, value in data.items():
                    if key in ['track', 'item', 'entity', 'data']:
                        result = self._extract_from_json_recursive(value, depth + 1)
                        if result:
                            return result
                            
            elif isinstance(data, list) and data:
                for item in data[:3]:
                    result = self._extract_from_json_recursive(item, depth + 1)
                    if result:
                        return result
        except Exception:
            pass
        return None

    @staticmethod
    def _parse_meta_tags(html_content: str, track_id: str):
        """Parsea meta tags del HTML"""
        try:
            patterns = {
                'title': r'<title>([^<]+)</title>',
                'og_title': r'<meta property="og:title" content="([^"]*)"',
                'og_image': r'<meta property="og:image" content="([^"]*)"'
            }
            
            extracted = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    extracted[key] = match.group(1).strip()
            
            title = extracted.get('og_title', '') or extracted.get('title', '')
            if title:
                title = re.sub(r'\s*\|\s*spotify.*$', '', title, flags=re.IGNORECASE)
                
                if ' by ' in title:
                    parts = title.split(' by ', 1)
                    return {
                        'name': parts[0].strip(),
                        'artist': parts[1].strip(),
                        'album': 'Unknown Album',
                        'image_url': extracted.get('og_image', ''),
                        'duration': 180,
                        'track_id': track_id
                    }
                elif ' - ' in title:
                    parts = title.split(' - ', 1)
                    return {
                        'name': parts[1].strip(),
                        'artist': parts[0].strip(),
                        'album': 'Unknown Album',
                        'image_url': extracted.get('og_image', ''),
                        'duration': 180,
                        'track_id': track_id
                    }
        except Exception:
            pass
        return None

    def _search_alternative_apis(self, track_id: str):
        """Método 3: APIs públicas alternativas"""
        try:
            # iTunes Search API
            url = "https://itunes.apple.com/search"
            params = {'term': track_id, 'media': 'music', 'entity': 'song', 'limit': 1}
            response = self.session.get(url, params=params, timeout=5) # type: ignore
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    track = data['results'][0]
                    return {
                        'name': track.get('trackName', f'Track {track_id}'),
                        'artist': track.get('artistName', 'Unknown Artist'),
                        'album': track.get('collectionName', 'Unknown Album'),
                        'duration': track.get('trackTimeMillis', 180000) // 1000,
                        'image_url': track.get('artworkUrl100', '').replace('100x100', '600x600'),
                        'track_id': track_id
                    }
        except Exception:
            pass
        return None


class Spotify2MP3Converter(BaseModel):
    ORIGIN_SPOTIFY = "spotify"
    
    def __init__(self):
        super().__init__(self.ORIGIN_SPOTIFY)
        self.current_track_id = None
        # Compartir el extractor (y su instancia de Spotdl) entre todos los conversores.
        # Spotdl usa SpotifyClient como singleton global, así que crear varias instancias
        # de Spotdl() causa conflictos. El singleton resuelve el problema.
        self.info_extractor = _get_shared_extractor()

    def get_supported_urls(self):
        """Retorna lista de patrones de URL soportados por Spotify"""
        return [
            r"https://open\.spotify\.com/(?:intl-\w+/)?track/[\w]+",
            r"https://open\.spotify\.com/(?:intl-\w+/)?album/[\w]+",
            r"https://open\.spotify\.com/(?:intl-\w+/)?playlist/[\w]+",
            r"spotify:track:[\w]+",
            r"spotify:album:[\w]+",
            r"spotify:playlist:[\w]+"
        ]

    def extract_spotify_id(self, url):
        """Extrae el ID de Spotify desde una URL"""
        # Limpiar parámetros de la URL (como ?si=...)
        url = url.split('?')[0]
        
        # Patrones para diferentes tipos de URL de Spotify (incluyendo URLs internacionales)
        patterns = [
            r"https://open\.spotify\.com/(?:intl-\w+/)?track/([a-zA-Z0-9]+)",
            r"https://open\.spotify\.com/(?:intl-\w+/)?album/([a-zA-Z0-9]+)",
            r"https://open\.spotify\.com/(?:intl-\w+/)?playlist/([a-zA-Z0-9]+)",
            r"spotify:track:([a-zA-Z0-9]+)",
            r"spotify:album:([a-zA-Z0-9]+)",
            r"spotify:playlist:([a-zA-Z0-9]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1), self._get_type_from_pattern(pattern)
        
        raise ValueError(f"URL de Spotify no válida: {url}")

    @staticmethod
    def _get_type_from_pattern(pattern):
        """Determina el tipo de contenido basado en el patrón"""
        if "track" in pattern:
            return "track"
        elif "album" in pattern:
            return "album"
        elif "playlist" in pattern:
            return "playlist"
        return "unknown"

    def get_track_info(self, spotify_url):
        """Obtiene información de una pista de Spotify"""
        try:
            print("🔍 Obteniendo información con métodos alternativos...")
            raw = self.info_extractor.get_track_info(spotify_url)

            if not raw:
                raise Exception("No se pudo obtener información con métodos alternativos")

            # Normalizar: la info puede venir en formato canónico (artista/titulo)
            # o en formato legacy (artist/name). Exponer AMBOS para que el resto
            # del código funcione sin importar cuál use.
            artist_v  = raw.get('artista') or raw.get('artist') or 'Unknown Artist'
            title_v   = raw.get('titulo')  or raw.get('name')   or 'Unknown'
            image_url = raw.get('caratula_url') or raw.get('image_url') or ''
            album_v   = raw.get('album', 'Unknown Album')
            dur_seg   = raw.get('duracion_seg') or raw.get('duration') or 0

            return {
                # Claves canónicas (usadas por convert())
                'titulo':           title_v,
                'artista':          artist_v,
                'caratula_url':     image_url,
                'duracion_seg':     dur_seg,
                'genero':           raw.get('genero', ''),
                'plataforma_origen': 'Spotify',
                'url_origen':       spotify_url,
                'ruta_local':       '',
                'letra':            raw.get('letra', ''),
                # Claves de compatibilidad (usadas por add_metadata_to_mp3,
                # search_on_youtube y BD-saving legacy)
                'name':             title_v,
                'artist':           artist_v,
                'artists':          [artist_v],
                'album':            album_v,
                'duration_ms':      dur_seg * 1000,
                'images':           [{'url': image_url}] if image_url else [],
                'image_url':        image_url,
            }

        except Exception as e:
            raise Exception(f"Error al obtener información de Spotify: {e}")

    def search_on_youtube(self, track_name, artist_name, expected_duration_s: int = 0):
        """Busca la pista en YouTube usando yt-dlp con múltiples estrategias"""

        # Si tenemos información específica, usarla
        if track_name and not track_name.startswith("Track ") and artist_name and artist_name != "Unknown Artist":
            search_queries = [
                f"{artist_name} - {track_name}",
                f"{track_name} {artist_name}",
                f'"{track_name}" "{artist_name}"'
            ]
        # Si solo tenemos información básica/limitada, usar ID de Spotify
        elif hasattr(self, 'current_track_id'):
            # Usar el ID de Spotify para búsquedas más específicas
            track_id = self.current_track_id
            search_queries = [
                f"spotify {track_id}",
                f"{track_name} music",
                f"{track_name} song",
                track_name if track_name else f"track {track_id}"
            ]
        else:
            search_queries = [f"{artist_name} - {track_name}"]
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch10:',  # 10 resultados para mejor selección
        }
        
        # Probar múltiples consultas de búsqueda
        for search_query in search_queries:
            try:
                print(f"🔍 Buscando: {search_query}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: # type: ignore
                    info = ydl.extract_info(search_query, download=False)
                    if info and 'entries' in info and info['entries']:
                        best_video = self._select_best_youtube_result(
                            info['entries'], track_name, artist_name,
                            expected_duration_s=expected_duration_s
                        )
                        
                        if best_video:
                            return {
                                'url': best_video['webpage_url'],
                                'title': best_video['title'],
                                'duration': best_video.get('duration', 0),
                                'uploader': best_video.get('uploader', '')
                            }
                            
            except Exception as e:
                print(f"⚠️ Error en búsqueda '{search_query}': {e}")
                continue
        
        raise Exception("No se encontraron resultados en YouTube")

    @staticmethod
    def _select_best_youtube_result(entries, track_name, artist_name, expected_duration_s: int = 0):
        """Selecciona el mejor resultado de YouTube basado en criterios de puntuación.
        
        Criterios principales (en orden de importancia):
        1. Proximidad a la duración real de Spotify (evita previews cortos)
        2. Presencia de título y artista en el nombre del vídeo
        3. Canal oficial (Topic, VEVO, etc.)
        4. Penalizaciones por palabras clave problemáticas
        """
        if not entries:
            return None

        scored_entries = []

        track_lower  = (track_name  or '').lower()
        artist_lower = (artist_name or '').lower()

        for entry in entries:
            if not entry:
                continue

            title      = (entry.get('title', '')       or '').lower()
            uploader   = (entry.get('uploader', '')    or '').lower()
            channel    = (entry.get('channel', '')     or '').lower()
            description= (entry.get('description', '') or '').lower()
            duration   = entry.get('duration', 0) or 0

            score = 0

            # ── 1. DURACIÓN (criterio más importante) ──────────────────────────
            if expected_duration_s > 0 and duration > 0:
                ratio = duration / expected_duration_s      # 1.0 = perfecto
                diff  = abs(duration - expected_duration_s)

                if ratio < 0.5:                            # Menos de la mitad → preview
                    score -= 60
                elif ratio < 0.75:                         # 25-50 % más corto
                    score -= 25
                elif 0.85 <= ratio <= 1.20:                # ±15 % del esperado
                    score += 50
                elif 0.75 <= ratio < 0.85 or 1.20 < ratio <= 1.40:
                    score += 20                            # ±15-40 % → aceptable
                elif ratio > 2.0:                          # Más del doble → mix/medley
                    score -= 20
            else:
                # Sin duración conocida: penalizar vídeos muy cortos
                if 0 < duration < 90:
                    score -= 30
                elif 90 <= duration <= 600:
                    score += 5

            # ── 2. TÍTULO / ARTISTA en el nombre del vídeo ────────────────────
            # Coincidencia exacta de palabras individuales (más robusta que substring)
            def word_overlap(text: str, query: str) -> int:
                if not query:
                    return 0
                words = [w for w in query.split() if len(w) > 2]
                return sum(1 for w in words if w in text)

            track_words  = word_overlap(title, track_lower)
            artist_words = word_overlap(title, artist_lower)
            total_words  = max(len([w for w in track_lower.split()  if len(w) > 2]), 1)
            artist_total = max(len([w for w in artist_lower.split() if len(w) > 2]), 1)

            score += min(track_words  / total_words,  1.0) * 20   # hasta +20
            score += min(artist_words / artist_total, 1.0) * 15   # hasta +15

            # ── 3. CANAL OFICIAL ───────────────────────────────────────────────
            uploader_and_channel = uploader + ' ' + channel
            # Canal Topic = subida automática de YouTube Music (suele ser la versión oficial)
            if uploader_and_channel.strip().endswith(' - topic') or ' - topic' in uploader_and_channel:
                score += 25
            # VEVO u otros sellos conocidos
            official_keywords = ['vevo', 'official', 'records', 'music', 'entertainment', 'productions']
            for kw in official_keywords:
                if kw in uploader_and_channel:
                    score += 8
                    break
            # «Provided to YouTube» en la descripción → subida por sello discográfico
            if 'provided to youtube' in description:
                score += 15
            if 'auto-generated by youtube' in description:
                score += 10

            # ── 4. PENALIZACIONES ─────────────────────────────────────────────
            hard_avoid = ['preview', 'teaser', 'snippet', 'clip oficial', 'short clip']
            for kw in hard_avoid:
                if kw in title:
                    score -= 30
                    break

            soft_avoid = ['cover', 'karaoke', 'instrumental', 'tutorial', 'reaction',
                          'review', 'ranking', 'top 10', 'hora', '1 hour', '10 hours']
            for kw in soft_avoid:
                if kw in title:
                    score -= 10

            # Live / concierto penalizar levemente (pueden ser versiones válidas)
            live_kws = ['live', 'concert', 'en vivo', 'acoustic', 'en directo']
            for kw in live_kws:
                if kw in title:
                    score -= 5

            scored_entries.append((score, entry))

        scored_entries.sort(key=lambda x: x[0], reverse=True)

        if scored_entries:
            best_entry = scored_entries[0][1]
            best_score = scored_entries[0][0]
            print(
                f"✅ Mejor resultado (score={best_score:.0f}): "
                f"{best_entry.get('title', 'Sin título')} "
                f"[{best_entry.get('duration', '?')}s]"
            )
            return best_entry

        return entries[0]  # Fallback al primer resultado

    @staticmethod
    def download_from_youtube(youtube_url, output_path, filename_tmpl=None):
        """Descarga audio desde YouTube usando yt-dlp.
        
        Si se pasa filename_tmpl (ej: '/ruta/Artista - Titulo.%(ext)s'),
        yt-dlp descarga directamente a ese nombre y se devuelve la ruta .mp3.
        Si no, usa %(title)s.%(ext)s y escanea el directorio como fallback.
        """
        import yt_dlp as yt_dlp_module
        from typing import Any, Dict

        outtmpl = filename_tmpl if filename_tmpl else os.path.join(output_path, '%(title)s.%(ext)s')

        ffmpeg_path = os.environ.get('EKHO_FFMPEG_PATH')
        if not ffmpeg_path and getattr(sys, 'frozen', False):
            ffmpeg_path = os.path.join(
                sys._MEIPASS,
                'imageio_ffmpeg', 'binaries',
                'ffmpeg-win-x86_64-v7.1.exe'
            )
        if not ffmpeg_path:
            ffmpeg_path = 'ffmpeg'
        ydl_opts: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp_module.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                ydl.download([youtube_url])

            # Si se indicó el nombre exacto, devolver esa ruta
            if filename_tmpl:
                # yt-dlp reemplaza %(ext)s → mp3 tras el postprocessor
                expected = os.path.splitext(filename_tmpl.replace('%(ext)s', 'mp3'))[0] + '.mp3'
                # Normalizar: quitar el '.%(ext)s' que puede quedar en el stem
                expected = filename_tmpl.replace('%(ext)s', 'mp3')
                if os.path.exists(expected):
                    return expected

            # Fallback: buscar el MP3 más reciente en output_path
            mp3s = sorted(
                [os.path.join(output_path, f) for f in os.listdir(output_path) if f.endswith('.mp3')],
                key=os.path.getmtime,
                reverse=True,
            )
            if mp3s:
                return mp3s[0]  # el más reciente = el recién descargado

            raise Exception("No se encontró el archivo MP3 descargado")
                
        except Exception as e:
            raise Exception(f"Error al descargar desde YouTube: {e}")

    @staticmethod
    def download_album_art(image_url, save_path):
        """Descarga la portada del álbum"""
        try:
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return save_path
            
        except Exception as e:
            print(f"⚠️ No se pudo descargar la portada: {e}")
            return None

    def add_metadata_to_mp3(self, file_path, track_info, album_art_path=None):
        """Añade metadatos al archivo MP3 usando mutagen"""
        try:
            print("🏷️ Añadiendo metadatos con mutagen...")
            
            audio = MP3(file_path, ID3=ID3) # type: ignore
            
            # Añadir tags básicos usando la nueva estructura de metadatos
            titulo = track_info.get('titulo', track_info.get('name', ''))
            artista = track_info.get('artista', ', '.join(track_info.get('artists', [])))
            album = track_info.get('album', track_info.get('album', {}).get('name', '') if isinstance(track_info.get('album'), dict) else track_info.get('album', ''))
            
            audio.tags.add(TIT2(encoding=3, text=titulo)) # type: ignore
            audio.tags.add(TPE1(encoding=3, text=artista)) # type: ignore
            audio.tags.add(TALB(encoding=3, text=album)) # type: ignore
            
            # Añadir portada si está disponible
            if album_art_path and os.path.exists(album_art_path):
                with open(album_art_path, 'rb') as img:
                    audio.tags.add(APIC( # type: ignore
                        encoding=3,
                        mime='image/jpeg',
                        type=3,
                        desc='Cover',
                        data=img.read()
                    ))
                print("🖼️ Portada agregada")
            
            audio.save()
            print("✅ Metadatos guardados")
                
        except Exception as e:
            print(f"⚠️ Error al añadir metadatos: {e}")

    def convert(self, spotify_url): # type: ignore
        """Convierte una URL de Spotify a MP3"""
        # Usar carpeta configurada (o la por defecto)
        downloads_dir = self.download_folder
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Extraer track_id para búsquedas mejoradas
        try:
            track_id, _ = self.extract_spotify_id(spotify_url)
            self.current_track_id = track_id
        except Exception:
            pass
        
        # 1. Obtener información de la pista de Spotify
        print("🔍 Obteniendo información de Spotify...")
        track_info = self.get_track_info(spotify_url)
        if not track_info:
            raise RuntimeError("No se pudo obtener información de la canción desde Spotify")
        
        titulo_final = track_info.get('titulo', track_info.get('name', 'desconocido'))
        artista_final = track_info.get('artista', track_info.get('artist', 'desconocido'))
        print(f"📀 Canción: {artista_final} - {titulo_final}")
        
        # 2. Buscar la pista en YouTube
        print("🔍 Buscando en YouTube...")
        spotify_duration_s = track_info.get('duracion_seg') or track_info.get('duration') or 0
        youtube_info = self.search_on_youtube(titulo_final, artista_final, expected_duration_s=int(spotify_duration_s))
        print(f"✅ Encontrado en YouTube: {youtube_info['title']}")
        
        # 3. Descargar desde YouTube
        safe_title_pre  = self._sanitize_filename(titulo_final)
        safe_artist_pre = self._sanitize_filename(artista_final)
        _outtmpl = os.path.join(downloads_dir, f"{safe_artist_pre} - {safe_title_pre}.%(ext)s")

        print("⬇️ Descargando desde YouTube...")
        mp3_path = self.download_from_youtube(youtube_info['url'], downloads_dir, filename_tmpl=_outtmpl)
        print(f"✅ Audio descargado: {mp3_path}")
        
        # 4. Descargar portada del álbum
        album_art_path = None
        cover_url = track_info.get('caratula_url') or track_info.get('image_url', '')
        if cover_url:
            print("🖼️ Descargando portada del álbum...")
            album_art_path = os.path.join(downloads_dir, "temp_cover.jpg")
            album_art_path = self.download_album_art(cover_url, album_art_path)
        
        # 5. Añadir metadatos de Spotify
        print("🏷️ Añadiendo metadatos...")
        self.add_metadata_to_mp3(mp3_path, track_info, album_art_path)
        
        # 6. Limpiar archivo temporal de portada
        if album_art_path and os.path.exists(album_art_path):
            try:
                os.remove(album_art_path)
            except Exception:
                pass
        
        # 7. Asegurar nombre final correcto
        safe_title  = self._sanitize_filename(titulo_final)
        safe_artist = self._sanitize_filename(artista_final)
        new_filename = f"{safe_artist} - {safe_title}.mp3"
        new_path = os.path.join(downloads_dir, new_filename)

        if os.path.abspath(mp3_path) != os.path.abspath(new_path):
            try:
                os.rename(mp3_path, new_path)
                mp3_path = new_path
            except Exception:
                pass
        
        print(f"✅ Conversión completada: {mp3_path}")

        # ── Guardar en BD ──────────────────────────────────────────────
        if _DB_ADAPTER_OK:
            try:
                _album = track_info.get('album', '')
                if isinstance(_album, dict):
                    _album = _album.get('name', '')
                # Leer duración real del archivo MP3 (fallback: duración de Spotify)
                try:
                    duracion_real = int(MP3(mp3_path).info.length)
                except Exception:
                    duracion_real = track_info.get('duracion_seg') or (track_info.get('duration_ms') or 0) // 1000

                metadata_bd = {
                    'titulo':            titulo_final,
                    'artista':           artista_final,
                    'album':             _album,
                    'duracion_seg':      duracion_real,
                    'plataforma_origen': 'Spotify',
                    'url_origen':        spotify_url,
                    'ruta_local':        os.path.abspath(mp3_path),
                    'caratula_url':      cover_url,
                }
                id_cancion = upsert_cancion(metadata_bd)
                registrar_descarga(id_cancion, formato='mp3')
            except Exception as _bd_err:
                print(f"⚠️ No se pudo guardar en BD: {_bd_err}")
        # ───────────────────────────────────────────────────────────────

        return mp3_path

    # ── Soporte de playlists / álbumes ──────────────────────────────────────

    @staticmethod
    def _normalize_spotify_url(url: str) -> str:
        """Elimina el prefijo de localización intl-xx/ de las URLs de Spotify.

        Ejemplo: open.spotify.com/intl-es/album/xxx → open.spotify.com/album/xxx
        """
        return re.sub(r'(open\.spotify\.com/)intl-\w+/', r'\1', url.strip())

    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """Devuelve True si la URL es una playlist o álbum de Spotify.
        Soporta URLs con prefijo intl-xx/ (p.ej. intl-es/album/...).
        """
        url = url.strip()
        # Manejo de URLs con localización (intl-es/, intl-pt/, etc.)
        if re.search(r'open\.spotify\.com/intl-\w+/(playlist|album)/', url):
            return True
        return ('open.spotify.com/playlist/' in url or
                'open.spotify.com/album/'    in url or
                'spotify:playlist:'          in url or
                'spotify:album:'             in url)

    def get_playlist_songs(self, url: str):
        """Devuelve lista de objetos Song de spotdl para una playlist/álbum."""
        if SPOTDL_API_MODE != 'legacy_spotdl_class':
            raise RuntimeError('La versión de spotdl instalada no soporta búsqueda de playlists')
        clean_url = self._normalize_spotify_url(url)
        songs = self.info_extractor.spotdl.search([clean_url])  # type: ignore
        if not songs:
            raise RuntimeError(f'No se encontraron canciones en: {clean_url}')
        return songs

    def _get_spotify_playlist_cover(self, url: str) -> str:
        """Obtiene la URL de portada de una playlist/álbum de Spotify via OEmbed (sin auth)."""
        clean_url = self._normalize_spotify_url(url)
        try:
            resp = requests.get(
                f'https://open.spotify.com/oembed?url={clean_url}',
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'},
            )
            if resp.status_code == 200:
                return resp.json().get('thumbnail_url', '')
        except Exception:
            pass
        return ''

    def convert_playlist(self, url: str, on_progress=None):
        """Descarga todas las canciones de una playlist/álbum de Spotify.

        Parámetros:
        - on_progress: callback(actual, total, titulo) llamado tras cada canción
        Devuelve lista de rutas de archivos descargados.
        """
        url = self._normalize_spotify_url(url)
        print(f'\n🎵 Obteniendo canciones de la playlist: {url}')
        songs = self.get_playlist_songs(url)
        total = len(songs)
        if total == 0:
            print('📋 0 canciones encontradas')
            return []

        # Metadatos de playlist
        playlist_name = getattr(songs[0], 'list_name', None) or 'Playlist Spotify'
        print(f'📋 {total} canciones en "{playlist_name}"')
        cover_url = self._get_spotify_playlist_cover(url)
        if not cover_url:
            cover_url = getattr(songs[0], 'cover_url', '') or ''

        results = []
        song_ids = []
        failed = 0
        for i, song in enumerate(songs, 1):
            titulo = getattr(song, 'name', '?')
            artistas = getattr(song, 'artists', []) or []
            artista = artistas[0] if artistas else '?'
            print(f'\n[{i}/{total}] {artista} - {titulo}')
            try:
                track_url = getattr(song, 'url', None)
                if not track_url:
                    song_id = getattr(song, 'song_id', None)
                    track_url = f'https://open.spotify.com/track/{song_id}' if song_id else None
                if not track_url:
                    print(f'  ⚠️  Sin URL, omitiendo')
                    failed += 1
                    continue
                path = self.convert(track_url)
                if path:
                    results.append(path)
                    print(f'  ✅ Descargado: {path}')
                    if _DB_ADAPTER_OK:
                        from model.db_adapter import get_id_cancion_por_ruta
                        id_c = get_id_cancion_por_ruta(path)
                        if id_c:
                            song_ids.append(id_c)
                else:
                    failed += 1
                    print(f'  ❌ Falló (sin ruta)')
            except Exception as e:
                print(f'  ❌ Error: {e}')
                failed += 1
            if on_progress:
                on_progress(i, total, titulo)

        # Crear playlist en BD con portada
        if song_ids and _DB_ADAPTER_OK:
            try:
                from model.db_adapter import guardar_playlist_json_completa
                guardar_playlist_json_completa(
                    id_usuario=1,
                    nombre=playlist_name,
                    descripcion=f'Importada de Spotify | {url}',
                    canciones=song_ids,
                    caratula_url=cover_url,
                )
            except Exception as _pl_err:
                print(f'⚠️ No se pudo crear la playlist en BD: {_pl_err}')

        print(f'\n🎉 Playlist completada: {len(results)}/{total} exitosas  ·  {failed} fallidas')
        return results

    # ────────────────────────────────────────────────────────────────────────

    def _update_metadata_with_local_path(self, track_info, local_path):
        """Actualiza los metadatos con la ruta local del archivo descargado"""
        try:
            filepath = self.info_extractor.get_metadata_file_path()
            if not os.path.exists(filepath):
                print("⚠️ Archivo de metadatos no encontrado")
                return
            
            # Leer archivo existente
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            track_id = track_info.get('track_id', '')
            
            # Actualizar en track_actual si coincide
            if data.get('track_actual', {}).get('track_id') == track_id:
                data['track_actual']['ruta_local'] = os.path.abspath(local_path)
                data['track_actual']['archivo_actualizado'] = datetime.datetime.now().isoformat()
            
            # Actualizar en la lista de tracks
            if 'tracks' in data:
                for i, track in enumerate(data['tracks']):
                    if track.get('track_id') == track_id:
                        data['tracks'][i]['ruta_local'] = os.path.abspath(local_path)
                        data['tracks'][i]['archivo_actualizado'] = datetime.datetime.now().isoformat()
                        break
            
            data['ultima_actualizacion'] = datetime.datetime.now().isoformat()
            
            # Guardar archivo actualizado
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Metadatos actualizados con ruta local: {local_path}")
                        
        except Exception as e:
            print(f"⚠️ Error en actualización de metadatos: {e}")
    
    def start_download_session(self, is_batch=False):
        """Inicia una nueva sesión de descarga (compatibilidad — ya no gestiona JSON)"""
        if is_batch:
            print("🎵 Iniciando descarga de álbum/playlist...")
        else:
            print("🎵 Iniciando descarga de canción individual...")
    
    def finish_download_session(self):
        """Finaliza la sesión de descarga"""
        if hasattr(self, '_batch_session_started'):
            delattr(self, '_batch_session_started')

    @staticmethod
    def _sanitize_filename(filename):
        """Limpia el nombre de archivo de caracteres no válidos"""
        # Remover caracteres no válidos para nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Limitar longitud
        return filename[:50] if len(filename) > 50 else filename


# ============================================================
# Función de conveniencia — misma interfaz que convert_youtube
# y convert_soundcloud
# ============================================================

def convert_spotify(url):
    """
    Función de conveniencia: entrega un link de Spotify y devuelve la ruta del MP3.
    Equivalente a Spotify2MP3Converter().convert(url).
    """
    converter = Spotify2MP3Converter()
    return converter.convert(url)