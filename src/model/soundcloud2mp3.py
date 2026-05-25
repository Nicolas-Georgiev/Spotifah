# soundcloud2mp3.py
"""
Conversor de SoundCloud a MP3 usando yt-dlp (API Python).
Patrón MVC — capa Model.  Sin subprocess; todo por API.
"""
import os
import sys
import re
import datetime
from pathlib import Path

# ── Asegurar que src/ esté en el path ──────────────────────────────────────
_src = os.path.dirname(os.path.abspath(__file__))
if _src not in sys.path:
    sys.path.insert(0, _src)

try:
    from frozen_utils import get_music_dir as _get_music_dir
except ImportError:
    def _get_music_dir():
        return str(Path(__file__).resolve().parent.parent.parent / "data" / "music")

# ── Adaptador de BD — importación segura ───────────────────────────────────
try:
    from model.db_adapter import upsert_cancion, registrar_descarga
    _DB_ADAPTER_OK = True
except Exception as _db_e:
    print(f"⚠️ soundcloud2mp3: db_adapter no disponible ({_db_e})")
    _DB_ADAPTER_OK = False

# ── yt-dlp ─────────────────────────────────────────────────────────────────
try:
    import yt_dlp
    _HAS_YTDLP_API = True
except ImportError:
    _HAS_YTDLP_API = False
    print("⚠️ yt-dlp no está instalado. Instálalo con: pip install yt-dlp")

# ── Mutagen para metadatos ─────────────────────────────────────────────────
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, ID3NoHeaderError
    from mutagen.id3._frames import APIC, TIT2, TPE1, TALB, COMM
    _HAS_MUTAGEN = True
except ImportError:
    _HAS_MUTAGEN = False

# ── Requests para portadas ─────────────────────────────────────────────────
try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


def _safe_filename(s: str) -> str:
    """Elimina caracteres no válidos para nombres de archivo."""
    s = re.sub(r'[\\/*?:"<>|]', '', s)
    return s.strip()[:120] or 'track'


class SoundCloudConverter:
    """Conversor de SoundCloud a MP3 usando yt-dlp Python API."""

    def __init__(self, download_folder: str = None):
        self.origin = "SoundCloud"
        if download_folder:
            self.download_folder = str(Path(download_folder).resolve())
        else:
            self.download_folder = str(Path(_get_music_dir()).resolve())
        Path(self.download_folder).mkdir(parents=True, exist_ok=True)

    def set_download_folder(self, path: str) -> None:
        abs_path = str(Path(path).resolve())
        Path(abs_path).mkdir(parents=True, exist_ok=True)
        self.download_folder = abs_path
        print(f"📁 Carpeta de descarga actualizada: {self.download_folder}")

    # ── Metadatos ─────────────────────────────────────────────────────────

    def _add_metadata(self, mp3_path: str, title: str, artist: str,
                      cover_url: str = None, album: str = None) -> None:
        """Incrusta metadatos ID3 y portada en el MP3 via mutagen."""
        if not _HAS_MUTAGEN:
            return
        try:
            try:
                tags = ID3(mp3_path)
            except ID3NoHeaderError:
                tags = ID3()

            tags[TIT2.__name__] = TIT2(encoding=3, text=title)
            tags[TPE1.__name__] = TPE1(encoding=3, text=artist)
            if album:
                tags[TALB.__name__] = TALB(encoding=3, text=album)
            tags[COMM.__name__] = COMM(
                encoding=3, lang='spa', desc='Origen',
                text=f'Descargado desde SoundCloud | {datetime.date.today()}'
            )

            if cover_url and _HAS_REQUESTS:
                try:
                    resp = _requests.get(cover_url, timeout=15)
                    if resp.status_code == 200 and resp.content:
                        mime = 'image/jpeg' if cover_url.lower().endswith(('.jpg', '.jpeg')) else 'image/jpeg'
                        tags[APIC.__name__] = APIC(
                            encoding=3, mime=mime,
                            type=3, desc='Cover', data=resp.content,
                        )
                except Exception as _ce:
                    print(f"⚠️ No se pudo descargar portada: {_ce}")

            tags.save(mp3_path, v2_version=3)
            print("✅ Metadatos añadidos correctamente")
        except Exception as e:
            print(f"⚠️ Error al añadir metadatos: {e}")

    # ── Descarga individual ────────────────────────────────────────────────

    def convert(self, url: str) -> str:
        """Descarga una pista de SoundCloud y devuelve la ruta del MP3."""
        if not _HAS_YTDLP_API:
            raise RuntimeError("yt-dlp no está disponible.")

        Path(self.download_folder).mkdir(parents=True, exist_ok=True)

        # 1. Obtener metadatos sin descargar
        meta_opts = {
            'quiet': True, 'skip_download': True,
            'no_warnings': True, 'extract_flat': False,
        }
        track_info = {}
        try:
            with yt_dlp.YoutubeDL(meta_opts) as ydl:
                track_info = ydl.extract_info(url, download=False) or {}
        except Exception as _me:
            print(f"⚠️ No se pudo obtener metadatos previos: {_me}")

        raw_title  = track_info.get('title') or track_info.get('track') or 'Unknown'
        raw_artist = (track_info.get('uploader') or track_info.get('artist') or
                      track_info.get('creator') or 'Unknown')
        duration   = track_info.get('duration')
        cover_url  = track_info.get('thumbnail') or track_info.get('artwork')
        genre      = track_info.get('genre') or ''

        safe_title  = _safe_filename(raw_title)
        safe_artist = _safe_filename(raw_artist)
        base_name   = f"{safe_artist} - {safe_title}"

        # 2. Descargar con nombre determinista (evita bug de archivo stale)
        outtmpl = str(Path(self.download_folder) / f"{base_name}.%(ext)s")
        expected_mp3 = str(Path(self.download_folder) / f"{base_name}.mp3")

        ffmpeg_path = os.environ.get('EKHO_FFMPEG_PATH')
        if not ffmpeg_path and getattr(sys, 'frozen', False):
            ffmpeg_path = os.path.join(
                sys._MEIPASS,
                'imageio_ffmpeg', 'binaries',
                'ffmpeg-win-x86_64-v7.1.exe'
            )
        if not ffmpeg_path:
            ffmpeg_path = 'ffmpeg'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': True,
            'noplaylist': True,
        }
        print(f"⬇️  Descargando: {raw_artist} - {raw_title}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 3. Verificar que el archivo existe
        mp3_path = expected_mp3
        if not Path(mp3_path).exists():
            # Fallback: el más reciente en la carpeta (nunca el primero alfabético)
            candidates = sorted(
                Path(self.download_folder).glob('*.mp3'),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if not candidates:
                raise FileNotFoundError(f"No se encontró MP3 tras descargar: {url}")
            mp3_path = str(candidates[0])
            print(f"ℹ️  Usando archivo más reciente: {mp3_path}")

        print(f"✅ Archivo: {mp3_path}")

        # 4. Metadatos ID3
        self._add_metadata(mp3_path, raw_title, raw_artist,
                           cover_url=cover_url, album=raw_artist)

        # 5. Guardar en BD
        if _DB_ADAPTER_OK:
            try:
                mp3_abs = os.path.normpath(os.path.abspath(mp3_path))
                # Leer duración real del archivo MP3 (fallback: duración de SoundCloud)
                try:
                    duracion_real = int(MP3(mp3_abs).info.length)
                except Exception:
                    duracion_real = int(duration) if duration else None

                metadata_bd = {
                    'titulo':            raw_title,
                    'artista':           raw_artist,
                    'duracion_seg':      duracion_real,
                    'genero':            genre or None,
                    'plataforma_origen': 'SoundCloud',
                    'url_origen':        url,
                    'ruta_local':        mp3_abs,
                    'caratula_url':      cover_url or None,
                }
                id_cancion = upsert_cancion(metadata_bd)
                registrar_descarga(id_cancion, formato='mp3')
            except Exception as _bd_err:
                print(f"⚠️ No se pudo guardar en BD: {_bd_err}")

        return mp3_path

    # ── Soporte de playlists / sets ────────────────────────────────────────

    @staticmethod
    def is_playlist_url(url: str) -> bool:
        """Devuelve True si la URL es un set/playlist de SoundCloud."""
        return 'soundcloud.com' in url and '/sets/' in url

    def get_playlist_track_urls(self, url: str) -> list:
        """Extrae las URLs individuales de pistas de un set de SoundCloud."""
        if not _HAS_YTDLP_API:
            return []
        ydl_opts = {
            'quiet': True, 'extract_flat': True,
            'skip_download': True, 'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info.get('entries', []) if info else []
        urls = []
        for e in entries:
            if not e:
                continue
            track_url = e.get('url') or e.get('webpage_url') or ''
            if 'soundcloud.com' in track_url:
                urls.append(track_url)
        return urls

    def get_playlist_info(self, url: str) -> dict:
        """Obtiene nombre y portada del set de SoundCloud."""
        if not _HAS_YTDLP_API:
            return {'nombre': 'Set SoundCloud', 'cover_url': ''}
        ydl_opts = {
            'quiet': True, 'extract_flat': True,
            'skip_download': True, 'no_warnings': True, 'playlistend': 1,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            return {
                'nombre': info.get('title') or 'Set SoundCloud',
                'cover_url': (info.get('thumbnail') or
                              info.get('artwork') or ''),
            }
        except Exception:
            return {'nombre': 'Set SoundCloud', 'cover_url': ''}

    def convert_playlist(self, url: str, on_progress=None) -> list:
        """Descarga todas las pistas de un set/playlist de SoundCloud.

        Parámetros:
        - on_progress: callback(actual, total, titulo) llamado tras cada canción
        Devuelve lista de rutas de archivos descargados.
        """
        print(f'\n🎵 Obteniendo pistas del set: {url}')
        pl_info = self.get_playlist_info(url)
        playlist_name = pl_info['nombre']
        cover_url     = pl_info['cover_url']
        print(f'📋 Set: {playlist_name}')

        track_urls = self.get_playlist_track_urls(url)
        total = len(track_urls)
        print(f'📋 {total} pistas encontradas')
        if total == 0:
            return []

        results  = []
        song_ids = []
        failed   = 0

        for i, track_url in enumerate(track_urls, 1):
            print(f'\n[{i}/{total}] {track_url}')
            try:
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
            except Exception as e:
                print(f'  ❌ Error: {e}')
                failed += 1
            if on_progress:
                on_progress(i, total, track_url)

        # Crear playlist en BD con portada
        if song_ids and _DB_ADAPTER_OK:
            try:
                from model.db_adapter import guardar_playlist_json_completa
                guardar_playlist_json_completa(
                    id_usuario=1,
                    nombre=playlist_name,
                    descripcion=f'Importada de SoundCloud | {url}',
                    canciones=song_ids,
                    caratula_url=cover_url,
                )
            except Exception as _pl_err:
                print(f'⚠️ No se pudo crear la playlist en BD: {_pl_err}')

        print(f'\n🎉 Set completado: {len(results)}/{total} exitosas  ·  {failed} fallidas')
        return results


# ── Función de conveniencia ────────────────────────────────────────────────

def convert_soundcloud(url: str, download_folder: str = "data/music") -> str:
    """
    Función de conveniencia: entrega un link de SoundCloud y devuelve la ruta del MP3.
    Equivalente a SoundCloudConverter(download_folder).convert(url).
    """
    return SoundCloudConverter(download_folder=download_folder).convert(url)
