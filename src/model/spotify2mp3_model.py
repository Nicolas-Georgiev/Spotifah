# spotify2mp3_model.py
import os
import re
import json
import requests
from .base_converter import BaseConverter

# Intentar múltiples bibliotecas de audio para conversión
HAS_CONVERSION = False
CONVERTER_TYPE = None

try:
    from moviepy.editor import AudioFileClip
    HAS_CONVERSION = True
    CONVERTER_TYPE = "moviepy"
    print("✅ Usando moviepy para conversión de audio")
except ImportError:
    try:
        from pydub import AudioSegment
        HAS_CONVERSION = True
        CONVERTER_TYPE = "pydub"
        print("✅ Usando pydub para conversión de audio")
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
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
    HAS_METADATA = True
    METADATA_TYPE = "mutagen"
    print("✅ Usando mutagen para metadatos de audio")
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

# Importar yt-dlp para descargar desde YouTube
try:
    import yt_dlp
    HAS_YT_DLP = True
    print("✅ Usando yt-dlp para descargas desde YouTube")
except ImportError:
    HAS_YT_DLP = False
    print("⚠️ yt-dlp no disponible. Instala: pip install yt-dlp")

# Importar spotdl para metadatos de Spotify (OBLIGATORIO)
try:
    from spotdl import Spotdl
    from spotdl.utils.config import get_config
    HAS_SPOTDL = True
    print("✅ Usando spotdl para metadatos de Spotify (REQUERIDO)")
except ImportError:
    HAS_SPOTDL = False
    print("🚨 ERROR: spotdl no disponible - ES OBLIGATORIO")
    print("   📦 INSTALAR: pip install spotdl")
    print("   ❌ El conversor de Spotify NO funcionará sin spotdl")

if not HAS_SPOTDL:
    print("\n🚨 CONFIGURACIÓN INCOMPLETA:")
    print("   spotdl es REQUERIDO para funcionalidad de Spotify")
    print("   Sin spotdl, solo funcionará el conversor de YouTube")

print("✅ Sistema optimizado: spotdl (OBLIGATORIO) + métodos alternativos como respaldo")


class SpotifyInfoExtractor:
    """Extrae información de Spotify usando spotdl como método principal y métodos alternativos como fallback"""
    
    def __init__(self):
        # SpotDL es OBLIGATORIO
        if not HAS_SPOTDL:
            raise ImportError("🚨 spotdl es REQUERIDO pero no está instalado. Ejecuta: pip install spotdl")
        
        # Configurar spotdl
        try:
            # Configurar spotdl con configuración básica válida
            self.spotdl = Spotdl(client_id=None, client_secret=None, 
                               user_auth=False)
            self.use_spotdl = True
            print("✅ SpotDL configurado exitosamente (MODO PRINCIPAL)")
        except Exception as e:
            print(f"🚨 Error CRÍTICO configurando SpotDL: {e}")
            print("   El conversor de Spotify NO funcionará")
            raise
        
        # Configurar sesión para métodos de respaldo (solo en caso de fallo de SpotDL)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_track_info(self, spotify_url: str):
        """Obtiene información de una pista usando el mejor método disponible"""
        track_id = self._extract_spotify_id(spotify_url)
        if not track_id:
            return None
        
        # Método PRINCIPAL: SpotDL (más confiable)
        if self.use_spotdl:
            track_info = self._get_info_from_spotdl(spotify_url)
            if track_info and track_info.get('artist') != 'Unknown Artist':
                print("✅ Metadatos obtenidos via SpotDL")
                return track_info
            else:
                print("⚠️ SpotDL falló, usando métodos alternativos...")
        
        # MÉTODOS ALTERNATIVOS (fallback)
        print("🔄 Usando métodos alternativos para extracción...")
        
        # Método 1: Página principal de Spotify
        track_info = self._get_info_from_main_page(track_id)
        if track_info and track_info.get('artist') != 'Unknown Artist':
            print("✅ Metadatos obtenidos via página principal")
            return track_info
        
        # Método 2: OEmbed público de Spotify
        track_info = self._get_info_from_oembed(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via OEmbed")
            return track_info
        
        # Método 3: Embed de Spotify
        track_info = self._get_info_from_embed(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via Embed")
            return track_info
        
        # Método 4: APIs públicas alternativas
        track_info = self._search_alternative_apis(track_id)
        if track_info:
            print("✅ Metadatos obtenidos via APIs alternativas")
            return track_info
        
        # Método 5: Información mínima (último recurso)
        print("⚠️ Usando información mínima como último recurso")
        return {
            'name': f'Track {track_id[:8]}',
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'image_url': '',
            'duration': 180,
            'track_id': track_id
        }

    def _get_info_from_spotdl(self, spotify_url: str):
        """Método PRINCIPAL: Extraer información usando SpotDL"""
        try:
            # Buscar la canción usando SpotDL
            songs = self.spotdl.search([spotify_url])
            
            if not songs or len(songs) == 0:
                print("⚠️ SpotDL: No se encontraron resultados")
                return None
            
            song = songs[0]  # Tomar el primer resultado
            
            # Extraer metadatos
            track_info = {
                'name': song.name or 'Unknown Title',
                'artist': ', '.join(song.artists) if song.artists else 'Unknown Artist', 
                'album': song.album_name or 'Unknown Album',
                'image_url': song.cover_url or '',
                'duration': int(song.duration or 180),
                'track_id': self._extract_spotify_id(spotify_url),
                'isrc': song.isrc or '',
                'release_date': song.date or '',
                'genres': song.genres or []
            }
            
            # Validar que tenemos información útil
            if (track_info['name'] != 'Unknown Title' and 
                track_info['artist'] != 'Unknown Artist' and
                len(track_info['artist']) > 1):
                return track_info
            else:
                print("⚠️ SpotDL: Metadatos incompletos")
                return None
                
        except Exception as e:
            print(f"⚠️ Error en SpotDL: {e}")
            return None

    def _extract_spotify_id(self, url: str):
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
            response = self.session.get(main_url, timeout=15)
            
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
    
    def _extract_album_from_html(self, html):
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
    
    def _extract_image_from_html(self, html):
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
            response = self.session.get(oembed_url, timeout=10)
            
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
            response = self.session.get(embed_url, timeout=10)
            
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

    def _parse_meta_tags(self, html_content: str, track_id: str):
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
            response = self.session.get(url, params=params, timeout=5)
            
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


class Spotify2MP3Converter(BaseConverter):
    def __init__(self):
        super().__init__(self.ORIGIN_SPOTIFY)
        self.info_extractor = SpotifyInfoExtractor()

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

    def _get_type_from_pattern(self, pattern):
        """Determina el tipo de contenido basado en el patrón"""
        if "track" in pattern:
            return "track"
        elif "album" in pattern:
            return "album"
        elif "playlist" in pattern:
            return "playlist"
        return "unknown"

    def get_track_info(self, spotify_url):
        """Obtiene información de una pista de Spotify usando métodos alternativos"""
        try:
            print("🔍 Obteniendo información con métodos alternativos...")
            track_info = self.info_extractor.get_track_info(spotify_url)
            
            if not track_info:
                raise Exception("No se pudo obtener información con métodos alternativos")
            
            # Convertir formato al formato esperado
            return {
                'name': track_info.get('name', 'Unknown'),
                'artists': [track_info.get('artist', 'Unknown Artist')],
                'album': track_info.get('album', 'Unknown Album'),
                'duration_ms': track_info.get('duration', 0) * 1000,
                'preview_url': None,
                'images': [{'url': track_info.get('image_url', '')}] if track_info.get('image_url') else []
            }
                
        except Exception as e:
            raise Exception(f"Error al obtener información de Spotify: {e}")

    def search_on_youtube(self, track_name, artist_name):
        """Busca la pista en YouTube usando yt-dlp con múltiples estrategias"""
        if not HAS_YT_DLP:
            raise ImportError("yt-dlp no está disponible. Instala con: pip install yt-dlp")

        # Estrategias de búsqueda mejoradas
        search_queries = []
        
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
            'default_search': 'ytsearch5:',  # Buscar 5 resultados para mejor selección
        }
        
        # Probar múltiples consultas de búsqueda
        for search_query in search_queries:
            try:
                print(f"🔍 Buscando: {search_query}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search_query, download=False)
                    if info and 'entries' in info and info['entries']:
                        # Filtrar resultados para encontrar el mejor match
                        best_video = self._select_best_youtube_result(
                            info['entries'], track_name, artist_name
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

    def _select_best_youtube_result(self, entries, track_name, artist_name):
        """Selecciona el mejor resultado de YouTube basado en criterios"""
        if not entries:
            return None
        
        # Si solo hay un resultado, devolverlo
        if len(entries) == 1:
            return entries[0]
        
        # Criterios de puntuación para seleccionar mejor resultado
        scored_entries = []
        
        for entry in entries:
            if not entry:
                continue
                
            title = entry.get('title', '').lower()
            uploader = entry.get('uploader', '').lower()
            duration = entry.get('duration', 0)
            
            score = 0
            
            # Penalizar videos muy cortos o muy largos
            if duration:
                if 30 <= duration <= 600:  # Entre 30 segundos y 10 minutos
                    score += 10
                elif duration > 600:
                    score -= 5
            
            # Bonificar si contiene las palabras de búsqueda
            if track_name and track_name.lower() in title:
                score += 15
            if artist_name and artist_name.lower() in title:
                score += 15
                
            # Bonificar si es de canal musical oficial
            music_keywords = ['official', 'music', 'records', 'entertainment']
            for keyword in music_keywords:
                if keyword in uploader:
                    score += 5
                    break
            
            # Penalizar covers, remixes, etc.
            avoid_keywords = ['cover', 'remix', 'live', 'concert', 'karaoke', 'instrumental']
            for keyword in avoid_keywords:
                if keyword in title:
                    score -= 3
            
            scored_entries.append((score, entry))
        
        # Ordenar por puntuación y devolver el mejor
        scored_entries.sort(key=lambda x: x[0], reverse=True)
        
        if scored_entries:
            best_entry = scored_entries[0][1]
            print(f"✅ Mejor resultado: {best_entry.get('title', 'Sin título')}")
            return best_entry
        
        return entries[0]  # Fallback al primer resultado

    def download_from_youtube(self, youtube_url, output_path, track_info):
        """Descarga audio desde YouTube usando yt-dlp"""
        if not HAS_YT_DLP:
            raise ImportError("yt-dlp no está disponible. Instala con: pip install yt-dlp")

        import yt_dlp as yt_dlp_module
        from typing import Any, Dict

        # Configuración para yt-dlp
        ydl_opts: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            with yt_dlp_module.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
                
                # Encontrar el archivo descargado
                for file in os.listdir(output_path):
                    if file.endswith('.mp3'):
                        return os.path.join(output_path, file)
                        
                raise Exception("No se encontró el archivo MP3 descargado")
                
        except Exception as e:
            raise Exception(f"Error al descargar desde YouTube: {e}")

    def download_album_art(self, image_url, save_path):
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
        """Añade metadatos al archivo MP3"""
        if not HAS_METADATA:
            print("⚠️ Sin bibliotecas de metadatos disponibles")
            return

        try:
            if METADATA_TYPE == "mutagen":
                self._add_metadata_mutagen(file_path, track_info, album_art_path)
            elif METADATA_TYPE == "eyed3":
                self._add_metadata_eyed3(file_path, track_info, album_art_path)
                
        except Exception as e:
            print(f"⚠️ Error al añadir metadatos: {e}")

    def _add_metadata_mutagen(self, file_path, track_info, album_art_path):
        """Añade metadatos usando mutagen"""
        audio = MP3(file_path, ID3=ID3)
        
        # Añadir tags básicos
        audio.tags.add(TIT2(encoding=3, text=track_info['name']))
        audio.tags.add(TPE1(encoding=3, text=", ".join(track_info['artists'])))
        audio.tags.add(TALB(encoding=3, text=track_info['album']))
        
        # Añadir portada si está disponible
        if album_art_path and os.path.exists(album_art_path):
            with open(album_art_path, 'rb') as img:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=img.read()
                ))
        
        audio.save()

    def _add_metadata_eyed3(self, file_path, track_info, album_art_path):
        """Añade metadatos usando eyed3"""
        audiofile = eyed3.load(file_path)
        if audiofile.tag is None:
            audiofile.initTag()
        
        audiofile.tag.title = track_info['name']
        audiofile.tag.artist = ", ".join(track_info['artists'])
        audiofile.tag.album = track_info['album']
        
        # Añadir portada si está disponible
        if album_art_path and os.path.exists(album_art_path):
            with open(album_art_path, 'rb') as img:
                audiofile.tag.images.set(3, img.read(), 'image/jpeg')
        
        audiofile.tag.save()

    def convert(self, spotify_url):
        """Convierte una URL de Spotify a MP3"""
        # Crear carpeta de descargas si no existe
        downloads_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "music")
        os.makedirs(downloads_dir, exist_ok=True)
        
        try:
            # Extraer track_id para búsquedas mejoradas
            try:
                track_id, _ = self.extract_spotify_id(spotify_url)
                self.current_track_id = track_id  # Guardar para búsquedas de YouTube
            except:
                self.current_track_id = None
            
            # 1. Obtener información de la pista de Spotify
            print("🔍 Obteniendo información de Spotify...")
            track_info = self.get_track_info(spotify_url)
            
            # 2. Buscar la pista en YouTube
            print("🔍 Buscando en YouTube...")
            youtube_info = self.search_on_youtube(
                track_info['name'], 
                track_info['artists'][0]
            )
            
            print(f"✅ Encontrado en YouTube: {youtube_info['title']}")
            
            # 3. Descargar desde YouTube
            print("⬇️ Descargando desde YouTube...")
            mp3_path = self.download_from_youtube(
                youtube_info['url'], 
                downloads_dir, 
                track_info
            )
            
            # 4. Descargar portada del álbum
            album_art_path = None
            if track_info['images']:
                print("🖼️ Descargando portada del álbum...")
                album_art_url = track_info['images'][0]['url']
                album_art_path = os.path.join(downloads_dir, "temp_cover.jpg")
                album_art_path = self.download_album_art(album_art_url, album_art_path)
            
            # 5. Añadir metadatos de Spotify
            print("🏷️ Añadiendo metadatos...")
            self.add_metadata_to_mp3(mp3_path, track_info, album_art_path)
            
            # 6. Limpiar archivo temporal de portada
            if album_art_path and os.path.exists(album_art_path):
                os.remove(album_art_path)
            
            # 7. Renombrar archivo con formato estándar
            safe_title = self._sanitize_filename(track_info['name'])
            safe_artist = self._sanitize_filename(track_info['artists'][0])
            new_filename = f"{safe_artist} - {safe_title}.mp3"
            new_path = os.path.join(downloads_dir, new_filename)
            
            if mp3_path != new_path:
                os.rename(mp3_path, new_path)
                mp3_path = new_path
            
            print(f"✅ Conversión completada: {mp3_path}")
            return mp3_path
            
        except Exception as e:
            raise Exception(f"Error en la conversión: {e}")

    def _sanitize_filename(self, filename):
        """Limpia el nombre de archivo de caracteres no válidos"""
        # Remover caracteres no válidos para nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Limitar longitud
        return filename[:50] if len(filename) > 50 else filename