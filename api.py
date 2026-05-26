import os
import stat
import sys
import json
import threading
import subprocess
import time

_src_dir = os.path.join(os.path.dirname(__file__), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    from model.spotify2mp3_model import Spotify2MP3Converter
    from model.youtube2mp3_model import YouTube2MP3Converter
    from model.soundcloud2mp3 import SoundCloudConverter
    from controller.music_controller import MusicController
    from model.music_library import MusicLibrary
    from databaseManager.db import Database


class Api:
    def __init__(self):
        self._project_root = os.path.dirname(os.path.abspath(__file__))
        self._is_frozen = getattr(sys, "frozen", False)

        self._data_dir = self._resolve_data_dir()
        self._music_dir = os.path.join(self._data_dir, "music")
        self._metadata_dir = os.path.join(self._data_dir, "metadata")
        self._bdd_dir = os.path.join(self._data_dir, "BDD")
        self._covers_dir = os.path.join(self._data_dir, "covers")
        self._settings_file = os.path.join(self._data_dir, "settings.json")

        os.makedirs(self._music_dir, exist_ok=True)
        os.makedirs(self._metadata_dir, exist_ok=True)
        os.makedirs(self._bdd_dir, exist_ok=True)
        os.makedirs(self._covers_dir, exist_ok=True)

        self._seed_ekho_db()

        self.db = Database(os.path.join(self._bdd_dir, "ekho.db"))
        self.library = MusicLibrary(self._music_dir)

        self._apply_settings()

        self._music_controller = None
        self._pygame_inited = False
        self._player_lock = threading.Lock()

        self._ensure_system_playlists()

        self._current_song_id = None

        self._import_tasks: dict[str, dict] = {}
        self._import_counter = 0

    def _resolve_data_dir(self):
        if self._is_frozen:
            if sys.platform == "win32":
                base = os.environ.get("APPDATA", os.path.expanduser("~"))
            elif sys.platform == "darwin":
                base = os.path.join(
                    os.path.expanduser("~"), "Library", "Application Support"
                )
            else:
                base = os.path.join(os.path.expanduser("~"), ".local", "share")
            return os.path.join(base, "EKHO", "data")
        return os.path.join(self._project_root, "data")

    def _seed_ekho_db(self):
        import shutil
        target = os.path.join(self._bdd_dir, "ekho.db")
        if os.path.exists(target):
            return
        seed = os.path.join(self._project_root, "data", "BDD", "ekho.db")
        if os.path.exists(seed):
            shutil.copy2(seed, target)

    def _ensure_system_playlists(self):
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id_playlist FROM playlists WHERE nombre = ? AND id_usuario = ?",
                    ("Favoritos", 1),
                )
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO playlists (id_usuario, nombre, descripcion, publica) VALUES (?, ?, ?, ?)",
                        (1, "Favoritos", "Tus canciones favoritas", 0),
                    )
                    conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

    def _ensure_favorites_playlist(self):
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id_playlist FROM playlists WHERE nombre = ? AND id_usuario = ?",
                    ("Favoritos", 1),
                )
                row = cur.fetchone()
                if row:
                    return row["id_playlist"]
                cur.execute(
                    "INSERT INTO playlists (id_usuario, nombre, descripcion, publica) VALUES (?, ?, ?, ?)",
                    (1, "Favoritos", "Tus canciones favoritas", 0),
                )
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()
        except Exception:
            return None

    # -- Cover extraction & local caching ------------------------

    def _localize_cover(self, song_id: int, external_url: str) -> str:
        if not external_url or external_url.startswith("/api/covers/"):
            return external_url
        try:
            url_lower = external_url.lower()
            ext = "jpg"
            for c in ["png", "webp", "jpeg", "gif"]:
                if f".{c}" in url_lower or f"image={c}" in url_lower:
                    ext = "jpeg" if c == "jpeg" else c
                    break
            local_url = f"/api/covers/{song_id}.{ext}"

            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT caratula_blob FROM canciones WHERE id_cancion = ?", (song_id,))
                row = cur.fetchone()
                if row and row["caratula_blob"]:
                    return local_url
            finally:
                conn.close()

            import urllib.request
            with urllib.request.urlopen(external_url) as response:
                image_data = response.read()

            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE canciones SET caratula_blob = ?, caratula_url = ? WHERE id_cancion = ?",
                    (image_data, local_url, song_id),
                )
                conn.commit()
            finally:
                conn.close()

            return local_url
        except Exception:
            return external_url

    def _ensure_cover(self, song_id: int, title: str, artist: str, album: str, mp3_path: str, plataforma: str) -> str:
        for meta_file in ["spotify_metadata.json", "youtube_metadata.json"]:
            meta_path = os.path.join(self._metadata_dir, meta_file)
            if not os.path.exists(meta_path):
                continue
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for track in data.get("tracks", []):
                    cover = track.get("caratula_url", "") or ""
                    if not cover:
                        continue
                    ruta_local = track.get("ruta_local", "") or ""
                    track_title = track.get("titulo", "") or ""
                    track_artist = track.get("artista", "") or ""
                    match = False
                    if ruta_local and mp3_path and os.path.normpath(ruta_local) == os.path.normpath(mp3_path):
                        match = True
                    elif track_title.lower() == title.lower() and track_artist.lower() == artist.lower():
                        match = True
                    elif track_title.lower() == title.lower() and album and track.get("album", "") and track["album"].lower() == album.lower():
                        match = True
                    if match:
                        return self._localize_cover(song_id, cover)
            except Exception:
                continue

        if mp3_path and os.path.exists(mp3_path):
            try:
                from mutagen.mp3 import MP3
                from mutagen.id3 import ID3, APIC
                audio = MP3(mp3_path)
                if audio.tags:
                    for tag in audio.tags.values():
                        if isinstance(tag, APIC):
                            ext = "jpg"
                            if tag.mime == "image/png":
                                ext = "png"
                            elif tag.mime == "image/webp":
                                ext = "webp"
                            local_url = f"/api/covers/{song_id}.{ext}"
                            conn = self.db.get_connection()
                            try:
                                cur = conn.cursor()
                                cur.execute(
                                    "UPDATE canciones SET caratula_blob = ?, caratula_url = ? WHERE id_cancion = ?",
                                    (tag.data, local_url, song_id),
                                )
                                conn.commit()
                            finally:
                                conn.close()
                            return local_url
            except Exception:
                pass

        return ""

    # -- Validación de dependencias -----------------------------

    def _check_ffmpeg(self) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True, ""
            return False, "ffmpeg no responde correctamente"
        except FileNotFoundError:
            return False, (
                "ffmpeg no está instalado. "
                "Descárgalo desde https://ffmpeg.org/download.html "
                "y asegúrate de que esté en el PATH del sistema"
            )
        except Exception as e:
            return False, f"Error al verificar ffmpeg: {e}"

    def _check_spotify_creds(self) -> tuple[bool, str]:
        client_id = os.getenv("SPOTIFY_CLIENT_ID") or os.getenv("SPOTDL_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET") or os.getenv("SPOTDL_CLIENT_SECRET")
        if not client_id or not client_secret:
            try:
                dotenv_path = os.path.join(self._project_root, '.env')
                if os.path.exists(dotenv_path):
                    with open(dotenv_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith('#') or '=' not in line:
                                continue
                            k, v = line.split('=', 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k in ('SPOTIFY_CLIENT_ID', 'SPOTDL_CLIENT_ID') and not client_id:
                                client_id = v
                            if k in ('SPOTIFY_CLIENT_SECRET', 'SPOTDL_CLIENT_SECRET') and not client_secret:
                                client_secret = v
            except Exception:
                pass
        if client_id and client_secret:
            return True, ""
        return False, (
            "SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET no configurados.\n"
            "Crea un archivo .env en la raíz del proyecto con:\n"
            "SPOTIFY_CLIENT_ID=tu_client_id\n"
            "SPOTIFY_CLIENT_SECRET=tu_client_secret\n"
            "o configúralos como variables de entorno."
        )

    # -- YouTube → MP3 ------------------------------------------

    def convert_youtube(self, url: str) -> dict:
        ok, msg = self._check_ffmpeg()
        if not ok:
            return {"ok": False, "error": msg}
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                converter = YouTube2MP3Converter()
                converter.set_download_folder(self._music_dir)
                result_path = converter.convert(url)
            return {
                "ok": True,
                "data": {
                    "path": result_path,
                    "filename": os.path.basename(result_path),
                    "log": f.getvalue(),
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "log": f.getvalue(),
            }

    # -- Spotify → MP3 -----------------------------------------

    def convert_spotify(self, url: str) -> dict:
        ok, msg = self._check_ffmpeg()
        if not ok:
            return {"ok": False, "error": msg}
        ok, msg = self._check_spotify_creds()
        if not ok:
            return {"ok": False, "error": msg}
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                converter = Spotify2MP3Converter()
                converter.set_download_folder(self._music_dir)
                result_path = converter.convert(url)
            return {
                "ok": True,
                "data": {
                    "path": result_path,
                    "filename": os.path.basename(result_path),
                    "log": f.getvalue(),
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "log": f.getvalue(),
            }

    # -- SoundCloud → MP3 ---------------------------------------

    def convert_soundcloud(self, url: str) -> dict:
        ok, msg = self._check_ffmpeg()
        if not ok:
            return {"ok": False, "error": msg}
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                converter = SoundCloudConverter(self._music_dir)
                result_path = converter.convert(url)
            if result_path is None:
                return {"ok": False, "error": "La conversión falló", "log": f.getvalue()}
            return {
                "ok": True,
                "data": {
                    "path": result_path,
                    "filename": os.path.basename(result_path),
                    "log": f.getvalue(),
                },
            }
        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "log": f.getvalue(),
            }

    # -- Importación de playlists ------------------------------

    # -- Album Preview --------------------------------------------

    def _cleanup_preview_covers(self):
        import glob
        for f in glob.glob(os.path.join(self._covers_dir, "preview_*.jpg")):
            try:
                os.remove(f)
            except Exception:
                pass

    def _localize_preview_cover(self, cover_url: str) -> str:
        if not cover_url or cover_url.startswith("/api/"):
            return cover_url
        self._cleanup_preview_covers()
        import hashlib, urllib.request
        h = hashlib.md5(cover_url.encode()).hexdigest()[:16]
        ext = "jpg"
        local = f"/api/covers/preview_{h}.{ext}"
        local_path = os.path.join(self._covers_dir, f"preview_{h}.{ext}")
        if os.path.exists(local_path):
            return local
        try:
            with urllib.request.urlopen(cover_url, timeout=10) as r:
                data = r.read()
            with open(local_path, "wb") as f:
                f.write(data)
            return local
        except Exception:
            return ''

    def delete_preview_cover(self, cover_url: str):
        if not cover_url:
            return
        import hashlib
        h = hashlib.md5(cover_url.encode()).hexdigest()[:16]
        local_path = os.path.join(self._covers_dir, f"preview_{h}.jpg")
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
        except Exception:
            pass

    def _get_spotify_album_preview(self, url: str) -> dict:
        from model.spotify2mp3_model import Spotify2MP3Converter

        converter = Spotify2MP3Converter()
        songs = converter.get_playlist_songs(url)
        if not songs:
            raise RuntimeError("No se encontraron canciones en el álbum")
        first = songs[0]
        cover_url = converter._get_spotify_playlist_cover(url)
        if not cover_url:
            cover_url = getattr(first, 'cover_url', '') or ''
        cover_url = self._localize_preview_cover(cover_url)

        is_album = '/album/' in url
        tracks = []
        for song in songs:
            artists = getattr(song, 'artists', []) or []
            tracks.append({
                "title": getattr(song, 'name', '?'),
                "artist": artists[0] if artists else '',
                "duration": getattr(song, 'duration', 0) or 0,
            })

        return {
            "platform": "spotify",
            "name": (getattr(first, 'list_name', None) or
                     getattr(first, 'album_name', None) or 'Álbum Spotify'),
            "artist": (getattr(first, 'album_artist', None) or
                       (getattr(first, 'artists', []) or [None])[0] or ''),
            "year": getattr(first, 'year', None),
            "cover_url": cover_url,
            "is_album": is_album,
            "total_tracks": len(tracks),
            "tracks": tracks,
        }

    def _get_youtube_album_preview(self, url: str) -> dict:
        from model.youtube2mp3_model import YouTube2MP3Converter
        import yt_dlp

        converter = YouTube2MP3Converter()
        info = converter.get_playlist_info(url)
        cover_url = info['cover_url']

        playlist_url = YouTube2MP3Converter._normalize_playlist_url(url)
        ydl_opts = {
            'quiet': True, 'extract_flat': True,
            'skip_download': True, 'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_data = ydl.extract_info(playlist_url, download=False)

        tracks = []
        entries = playlist_data.get('entries', []) if playlist_data else []
        for e in entries:
            if not e:
                continue
            tracks.append({
                "title": e.get('title', '?'),
                "artist": e.get('channel', '') or e.get('uploader', '') or '',
                "duration": e.get('duration', 0) or 0,
            })

        if not cover_url and entries:
            first_id = entries[0].get('id') if entries[0] else None
            if first_id:
                cover_url = f'https://i.ytimg.com/vi/{first_id}/hqdefault.jpg'

        return {
            "platform": "youtube",
            "name": info['nombre'],
            "artist": '',
            "year": None,
            "cover_url": self._localize_preview_cover(cover_url),
            "is_album": False,
            "total_tracks": len(tracks),
            "tracks": tracks,
        }

    def _get_soundcloud_album_preview(self, url: str) -> dict:
        import yt_dlp

        converter = SoundCloudConverter(self._music_dir)
        info = converter.get_playlist_info(url)
        ydl_opts = {
            'quiet': True, 'extract_flat': False,
            'skip_download': True, 'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_data = ydl.extract_info(url, download=False)

        cover_url = (playlist_data.get('thumbnail') or
                     playlist_data.get('artwork_url') or
                     playlist_data.get('artwork') or
                     info.get('cover_url') or '')

        tracks = []
        entries = playlist_data.get('entries', []) if playlist_data else []
        for e in entries:
            if not e:
                continue
            tracks.append({
                "title": e.get('title') or e.get('track') or '?',
                "artist": e.get('uploader', '') or '',
                "duration": e.get('duration', 0) or 0,
            })

        if not cover_url and entries:
            first = entries[0]
            if first:
                cover_url = (first.get('artwork_url') or
                             first.get('artwork') or
                             first.get('thumbnail') or '')

        return {
            "platform": "soundcloud",
            "name": info['nombre'],
            "artist": '',
            "year": None,
            "cover_url": self._localize_preview_cover(cover_url),
            "is_album": False,
            "total_tracks": len(tracks),
            "tracks": tracks,
        }

    def get_album_preview(self, url: str) -> dict:
        detection = self._detect_url_type(url)
        if not detection["platform"] or not detection["is_playlist"]:
            return {"ok": False, "error": "La URL no corresponde a un álbum o playlist válida"}
        if detection["platform"] == "spotify":
            ok, msg = self._check_spotify_creds()
            if not ok:
                return {"ok": False, "error": msg}
        try:
            if detection["platform"] == "spotify":
                preview = self._get_spotify_album_preview(url)
            elif detection["platform"] == "youtube":
                preview = self._get_youtube_album_preview(url)
            elif detection["platform"] == "soundcloud":
                preview = self._get_soundcloud_album_preview(url)
            else:
                return {"ok": False, "error": "Plataforma no soportada"}
            return {"ok": True, "data": preview}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def import_album(self, url: str) -> dict:
        return self.import_playlist(url)

    # -- Importación de playlists ------------------------------

    def _detect_url_type(self, url: str) -> dict:
        from model.spotify2mp3_model import Spotify2MP3Converter
        from model.youtube2mp3_model import YouTube2MP3Converter
        from model.soundcloud2mp3 import SoundCloudConverter

        if Spotify2MP3Converter.is_playlist_url(url):
            return {"platform": "spotify", "is_playlist": True}
        if YouTube2MP3Converter.is_playlist_url(url):
            return {"platform": "youtube", "is_playlist": True}
        if SoundCloudConverter.is_playlist_url(url):
            return {"platform": "soundcloud", "is_playlist": True}

        u = url.lower()
        if "youtube.com" in u or "youtu.be" in u:
            return {"platform": "youtube", "is_playlist": False}
        if "spotify.com" in u or "spotify:" in u:
            return {"platform": "spotify", "is_playlist": False}
        if "soundcloud.com" in u:
            return {"platform": "soundcloud", "is_playlist": False}
        return {"platform": None, "is_playlist": False}

    def detect_url_type(self, url: str) -> dict:
        return self._detect_url_type(url)

    def import_playlist(self, url: str) -> dict:
        detection = self._detect_url_type(url)
        if not detection["platform"] or not detection["is_playlist"]:
            return {"ok": False, "error": "La URL no corresponde a una playlist v\u00e1lida"}

        task_id = f"pl_{int(time.time())}_{self._import_counter}"
        self._import_counter += 1

        self._import_tasks[task_id] = {
            "status": "starting",
            "platform": detection["platform"],
            "url": url,
            "current": 0,
            "total": 0,
            "playlist_name": "",
            "playlist_id": None,
            "error": None,
            "log": "",
        }

        def _run():
            log_buf = io.StringIO()
            task = self._import_tasks[task_id]
            try:
                with contextlib.redirect_stdout(log_buf), contextlib.redirect_stderr(log_buf):
                    task["status"] = "running"

                    ok, msg = self._check_ffmpeg()
                    if not ok:
                        raise RuntimeError(msg)

                    if detection["platform"] == "spotify":
                        ok, msg = self._check_spotify_creds()
                        if not ok:
                            raise RuntimeError(msg)
                        converter = Spotify2MP3Converter()
                        self._import_spotify_playlist(task, converter, url)
                    elif detection["platform"] == "youtube":
                        converter = YouTube2MP3Converter()
                        self._import_youtube_playlist(task, converter, url)
                    elif detection["platform"] == "soundcloud":
                        converter = SoundCloudConverter(self._music_dir)
                        self._import_soundcloud_playlist(task, converter, url)

                    if task["status"] != "error":
                        task["status"] = "done"
            except Exception as e:
                task["status"] = "error"
                task["error"] = str(e)
            finally:
                task["log"] = log_buf.getvalue()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        return {"ok": True, "data": {"task_id": task_id, "platform": detection["platform"]}}

    def _import_spotify_playlist(self, task: dict, converter, url: str):
        songs = converter.get_playlist_songs(url)
        total = len(songs)
        task["total"] = total
        task["playlist_name"] = getattr(songs[0], 'list_name', None) or 'Playlist Spotify'
        print(f"Obteniendo {total} canciones de: {task['playlist_name']}")

        from model.db_adapter import get_id_cancion_por_ruta

        cover_url = converter._get_spotify_playlist_cover(url)
        if not cover_url:
            cover_url = getattr(songs[0], 'cover_url', '') or ''

        song_ids = []
        for i, song in enumerate(songs, 1):
            titulo = getattr(song, 'name', '?')
            artistas = getattr(song, 'artists', []) or []
            artista = artistas[0] if artistas else '?'
            print(f"[{i}/{total}] {artista} - {titulo}")
            try:
                track_url = getattr(song, 'url', None)
                if not track_url:
                    sid = getattr(song, 'song_id', None)
                    track_url = f'https://open.spotify.com/track/{sid}' if sid else None
                if track_url:
                    path = converter.convert(track_url)
                    if path:
                        id_c = get_id_cancion_por_ruta(path)
                        if id_c:
                            song_ids.append(id_c)
            except Exception as e:
                print(f"  Error: {e}")
            task["current"] = i

        self._finalize_import(task, song_ids, cover_url, url, "Spotify")

    def _import_youtube_playlist(self, task: dict, converter, url: str):
        pl_info = converter.get_playlist_info(url)
        task["playlist_name"] = pl_info["nombre"]
        cover_url = pl_info["cover_url"]

        track_urls = converter.get_playlist_track_urls(url)
        total = len(track_urls)
        task["total"] = total
        print(f"Obteniendo {total} v\u00eddeos de: {task['playlist_name']}")

        from model.db_adapter import get_id_cancion_por_ruta

        song_ids = []
        for i, track_url in enumerate(track_urls, 1):
            print(f"[{i}/{total}] {track_url}")
            try:
                path = converter.convert(track_url)
                if path:
                    id_c = get_id_cancion_por_ruta(path)
                    if id_c:
                        song_ids.append(id_c)
            except Exception as e:
                print(f"  Error: {e}")
            task["current"] = i

        if not cover_url and song_ids:
            from model.db_adapter import get_cancion_json
            primera = get_cancion_json(id_cancion=song_ids[0])
            if primera and primera.get("caratula_url"):
                cover_url = primera["caratula_url"]
                print(f"[COVER] Usando portada de la primera canci\u00f3n: {cover_url}")

        self._finalize_import(task, song_ids, cover_url, url, "YouTube")

    def _import_soundcloud_playlist(self, task: dict, converter, url: str):
        pl_info = converter.get_playlist_info(url)
        task["playlist_name"] = pl_info["nombre"]
        cover_url = pl_info["cover_url"]

        track_urls = converter.get_playlist_track_urls(url)
        total = len(track_urls)
        task["total"] = total
        print(f"Obteniendo {total} pistas de: {task['playlist_name']}")

        from model.db_adapter import get_id_cancion_por_ruta

        song_ids = []
        for i, track_url in enumerate(track_urls, 1):
            print(f"[{i}/{total}] {track_url}")
            try:
                path = converter.convert(track_url)
                if path:
                    id_c = get_id_cancion_por_ruta(path)
                    if id_c:
                        song_ids.append(id_c)
            except Exception as e:
                print(f"  Error: {e}")
            task["current"] = i

        if not cover_url and song_ids:
            from model.db_adapter import get_cancion_json
            primera = get_cancion_json(id_cancion=song_ids[0])
            if primera and primera.get("caratula_url"):
                cover_url = primera["caratula_url"]
                print(f"[COVER] Usando portada de la primera canci\u00f3n: {cover_url}")

        self._finalize_import(task, song_ids, cover_url, url, "SoundCloud")

    def _finalize_import(self, task: dict, song_ids: list, cover_url: str, url: str, platform_name: str):
        if not song_ids:
            task["status"] = "error"
            task["error"] = "No se pudo importar ninguna canci\u00f3n"
            return

        from model.db_adapter import guardar_playlist_json_completa
        result = guardar_playlist_json_completa(
            id_usuario=1,
            nombre=task["playlist_name"],
            descripcion=f'Importada de {platform_name} ',
            canciones=song_ids,
            caratula_url=cover_url,
        )
        if result:
            task["playlist_id"] = result.get("id_playlist")
            print(f"Playlist creada: {task['playlist_name']} (ID: {task['playlist_id']}, {len(song_ids)} canciones)")
        else:
            task["status"] = "error"
            task["error"] = "No se pudo guardar la playlist en la base de datos"

    def get_import_progress(self, task_id: str) -> dict:
        task = self._import_tasks.get(task_id)
        if not task:
            return {"ok": False, "error": "Tarea no encontrada"}
        return {
            "ok": True,
            "data": {
                "status": task["status"],
                "platform": task["platform"],
                "current": task["current"],
                "total": task["total"],
                "playlist_name": task["playlist_name"],
                "playlist_id": task["playlist_id"],
                "error": task["error"],
                "log": task["log"],
            },
        }

    # -- Playlists ----------------------------------------------

    def _playlist_cover_url(self, playlist_id: int) -> str:
        conn = self.db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT caratula_blob FROM playlists WHERE id_playlist = ?", (playlist_id,))
            row = cur.fetchone()
            if row and row["caratula_blob"]:
                return f"/api/playlist-covers/{playlist_id}.jpg"
        except Exception:
            pass
        finally:
            conn.close()
        return ""

    def get_playlists(self) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id_playlist, nombre, descripcion, publica FROM playlists ORDER BY id_playlist"
                )
                playlists = []
                for row in cur.fetchall():
                    pid = str(row["id_playlist"])
                    cover = self._playlist_cover_url(row["id_playlist"])
                    if not cover and row["nombre"] == "Favoritos":
                        cover = "/portadas/favorites.svg"
                    playlists.append({
                        "id": pid,
                        "name": row["nombre"],
                        "description": row["descripcion"] or "",
                        "is_public": bool(row["publica"]),
                        "cover_url": cover,
                    })
                playlists.insert(
                    0,
                    {
                        "id": "all",
                        "name": "Todas mis canciones",
                        "description": "Todas las canciones en tu biblioteca",
                        "is_public": False,
                        "cover_url": "/portadas/all-songs.svg",
                    },
                )
                return playlists
            finally:
                conn.close()
        except Exception:
            return [
                {
                    "id": "all",
                    "name": "Todas mis canciones",
                    "description": "",
                    "is_public": False,
                    "cover_url": "/portadas/all-songs.svg",
                }
            ]

    def get_playlist_songs(self, playlist_id: str) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                if playlist_id == "all":
                    cur.execute(
                        """SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                                  c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url,
                                  d.fecha_descarga
                           FROM canciones c
                           LEFT JOIN (
                               SELECT id_cancion, MAX(fecha_descarga) as fecha_descarga
                               FROM descargas GROUP BY id_cancion
                           ) d ON c.id_cancion = d.id_cancion
                           ORDER BY c.titulo"""
                    )
                else:
                    cur.execute(
                        """SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                                  c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url,
                                  d.fecha_descarga
                           FROM playlist_canciones pc
                           JOIN canciones c ON pc.id_cancion = c.id_cancion
                           LEFT JOIN (
                               SELECT id_cancion, MAX(fecha_descarga) as fecha_descarga
                               FROM descargas GROUP BY id_cancion
                           ) d ON c.id_cancion = d.id_cancion
                           WHERE pc.id_playlist = ?
                           ORDER BY pc.orden""",
                        (int(playlist_id),),
                    )
                rows = cur.fetchall()
                result = []
                for row in rows:
                    song_id = row["id_cancion"]
                    cover_url = row["caratula_url"] or ""
                    if not cover_url:
                        cover_url = self._ensure_cover(
                            song_id=song_id,
                            title=row["titulo"],
                            artist=row["artista"] or "",
                            album=row["album"] or "",
                            mp3_path=row["ruta_local"] or "",
                            plataforma=row["plataforma_origen"] or "",
                        )
                    cover_url = self._localize_cover(song_id, cover_url)
                    fecha_descarga = row["fecha_descarga"] or ""
                    is_downloaded = bool(fecha_descarga) and os.path.exists(row["ruta_local"] or "")
                    result.append({
                        "id": str(song_id),
                        "title": row["titulo"],
                        "artist": row["artista"] or "",
                        "album": row["album"] or "",
                        "duration": row["duracion_seg"] or 0,
                        "genre": row["genero"] or "",
                        "source": row["plataforma_origen"] or "",
                        "path": row["ruta_local"] or "",
                        "cover_url": cover_url,
                        "is_downloaded": is_downloaded,
                        "download_date": fecha_descarga,
                    })
                return result
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_songs(self) -> list:
        return self.get_playlist_songs("all")

    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (int(playlist_id), int(song_id)),
                )
                already = cur.fetchone() is not None
                if already:
                    return {
                        "ok": True,
                        "data": {
                            "message": "La cancion ya esta en la playlist",
                            "already_exists": True,
                        },
                    }
                cur.execute(
                    "SELECT COALESCE(MAX(orden), 0) + 1 FROM playlist_canciones WHERE id_playlist = ?",
                    (int(playlist_id),),
                )
                next_order = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO playlist_canciones (id_playlist, id_cancion, orden) VALUES (?, ?, ?)",
                    (int(playlist_id), int(song_id), next_order),
                )
                conn.commit()
                return {
                    "ok": True,
                    "data": {
                        "message": "Cancion anadida a la playlist",
                        "already_exists": False,
                    },
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (int(playlist_id), int(song_id)),
                )
                conn.commit()
                return {
                    "ok": True,
                    "data": {"message": "Cancion eliminada de la playlist"},
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_song(self, song_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT ruta_local FROM canciones WHERE id_cancion = ?", (int(song_id),))
                row = cur.fetchone()
                file_path = row["ruta_local"] if row else None

                deleted = False
                if file_path:
                    if os.path.exists(file_path):
                        try:
                            os.chmod(file_path, stat.S_IWRITE)
                            os.remove(file_path)
                            deleted = True
                        except Exception as e:
                            print(f"delete_song: no se pudo eliminar {file_path}: {e}")

                    if not deleted:
                        filename = os.path.basename(file_path)
                        alt_path = os.path.join(self._music_dir, filename)
                        if alt_path != file_path and os.path.exists(alt_path):
                            try:
                                os.chmod(alt_path, stat.S_IWRITE)
                                os.remove(alt_path)
                                deleted = True
                            except Exception as e:
                                print(f"delete_song: fallback tampoco funciono para {alt_path}: {e}")

                cur.execute("DELETE FROM playlist_canciones WHERE id_cancion = ?", (int(song_id),))
                cur.execute("DELETE FROM historial_reproduccion WHERE id_cancion = ?", (int(song_id),))
                cur.execute("DELETE FROM canciones WHERE id_cancion = ?", (int(song_id),))
                conn.commit()

                if hasattr(self, '_music_controller') and self._music_controller:
                    self._music_controller.remove_from_queue(int(song_id))

                return {"ok": True, "data": {"message": "Cancion eliminada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def update_song(self, song_id: str, data: dict) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                updates = []
                params = []

                field_mapping = {
                    "title": "titulo",
                    "artist": "artista",
                    "album": "album",
                    "genre": "genero",
                }

                for frontend_field, db_column in field_mapping.items():
                    if frontend_field in data:
                        updates.append(f"{db_column} = ?")
                        params.append(data[frontend_field].strip())

                if "cover_base64" in data and data["cover_base64"]:
                    try:
                        import base64
                        cover_data = data["cover_base64"]
                        if "," in cover_data:
                            cover_data = cover_data.split(",")[1]
                        cover_blob = base64.b64decode(cover_data)
                        updates.append("caratula_blob = ?")
                        params.append(cover_blob)
                        local_url = f"/api/covers/{int(song_id)}.jpg"
                        updates.append("caratula_url = ?")
                        params.append(local_url)
                    except Exception as e:
                        return {"ok": False, "error": f"Error al procesar imagen: {str(e)}"}

                if not updates:
                    return {"ok": False, "error": "No hay campos para actualizar"}

                params.append(int(song_id))
                query = f"UPDATE canciones SET {', '.join(updates)} WHERE id_cancion = ?"
                cur.execute(query, params)
                conn.commit()

                return {"ok": True, "data": {"message": "Canción actualizada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # -- Playlist CRUD -----------------------------------------

    def create_playlist(self, name: str, description: str = "") -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO playlists (id_usuario, nombre, descripcion, publica) VALUES (?, ?, ?, ?)",
                    (1, name.strip(), description.strip(), 0),
                )
                conn.commit()
                new_id = cur.lastrowid
                return {
                    "ok": True,
                    "data": {
                        "id": str(new_id),
                        "name": name.strip(),
                        "description": description.strip(),
                        "is_public": False,
                    },
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_playlist(self, playlist_id: str) -> dict:
        if playlist_id == "all":
            return {"ok": False, "error": "No se puede eliminar esta playlist"}
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM playlists WHERE id_playlist = ?", (int(playlist_id),))
                row = cur.fetchone()
                if not row:
                    return {"ok": False, "error": "Playlist no encontrada"}
                if row["nombre"] == "Favoritos":
                    return {"ok": False, "error": "No se puede eliminar la playlist de favoritos"}
                cur.execute("DELETE FROM playlists WHERE id_playlist = ?", (int(playlist_id),))
                conn.commit()
                return {"ok": True, "data": {"message": "Playlist eliminada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def rename_playlist(self, playlist_id: str, name: str, description: str = "", cover_base64: str = None) -> dict:
        if playlist_id == "all":
            return {"ok": False, "error": "No se puede renombrar esta playlist"}
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM playlists WHERE id_playlist = ?", (int(playlist_id),))
                row = cur.fetchone()
                if not row:
                    return {"ok": False, "error": "Playlist no encontrada"}
                if row["nombre"] == "Favoritos":
                    return {"ok": False, "error": "No se puede renombrar la playlist de favoritos"}

                import base64
                updates = ["nombre = ?", "descripcion = ?"]
                params = [name.strip(), description.strip()]

                if cover_base64:
                    try:
                        cover_data = cover_base64
                        if "," in cover_data:
                            cover_data = cover_data.split(",")[1]
                        cover_blob = base64.b64decode(cover_data)
                        updates.append("caratula_blob = ?")
                        params.append(cover_blob)
                    except Exception:
                        return {"ok": False, "error": "Error al procesar la imagen de portada"}

                params.append(int(playlist_id))
                cur.execute(
                    f"UPDATE playlists SET {', '.join(updates)} WHERE id_playlist = ?",
                    params,
                )
                conn.commit()
                return {"ok": True, "data": {"message": "Playlist actualizada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def search_songs(self, query: str) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                pattern = f"%{query}%"
                cur.execute(
                    """SELECT id_cancion, titulo, artista, album, duracion_seg,
                              genero, plataforma_origen, ruta_local, caratula_url
                       FROM canciones
                       WHERE titulo LIKE ? OR artista LIKE ? OR album LIKE ?
                       ORDER BY titulo LIMIT 50""",
                    (pattern, pattern, pattern),
                )
                rows = cur.fetchall()
                result = []
                for row in rows:
                    sid = row["id_cancion"]
                    cover = row["caratula_url"] or ""
                    if not cover:
                        cover = self._ensure_cover(sid, row["titulo"], row["artista"] or "", row["album"] or "", row["ruta_local"] or "", row["plataforma_origen"] or "")
                    cover = self._localize_cover(sid, cover)
                    result.append({
                        "id": str(sid),
                        "title": row["titulo"],
                        "artist": row["artista"] or "",
                        "album": row["album"] or "",
                        "duration": row["duracion_seg"] or 0,
                        "genre": row["genero"] or "",
                        "source": row["plataforma_origen"] or "",
                        "path": row["ruta_local"] or "",
                        "cover_url": cover,
                    })
                return result
            finally:
                conn.close()
        except Exception:
            return []

    def toggle_favorite(self, song_id: str) -> dict:
        try:
            fav_id = self._ensure_favorites_playlist()
            if not fav_id:
                return {"ok": False, "error": "No se pudo obtener la playlist de favoritos"}
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (fav_id, int(song_id)),
                )
                is_fav = cur.fetchone() is not None
                if is_fav:
                    cur.execute(
                        "DELETE FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                        (fav_id, int(song_id)),
                    )
                else:
                    cur.execute(
                        "SELECT COALESCE(MAX(orden), 0) + 1 FROM playlist_canciones WHERE id_playlist = ?",
                        (fav_id,),
                    )
                    nxt = cur.fetchone()[0]
                    cur.execute(
                        "INSERT INTO playlist_canciones (id_playlist, id_cancion, orden) VALUES (?, ?, ?)",
                        (fav_id, int(song_id), nxt),
                    )
                conn.commit()
                return {"ok": True, "data": {"favorite": not is_fav}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def is_favorite(self, song_id: str) -> dict:
        try:
            fav_id = self._ensure_favorites_playlist()
            if not fav_id:
                return {"ok": True, "data": {"favorite": False}}
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (fav_id, int(song_id)),
                )
                is_fav = cur.fetchone() is not None
                return {"ok": True, "data": {"favorite": is_fav}}
            finally:
                conn.close()
        except Exception:
            return {"ok": True, "data": {"favorite": False}}

    # -- Playback -----------------------------------------------

    def _init_player(self):
        if not self._pygame_inited:
            import pygame

            pygame.mixer.init()
            self.library = MusicLibrary(self._music_dir)
            self._music_controller = MusicController(self.library)
            settings = self.get_settings()
            saved_volume = settings.get("volume", 100)
            pygame.mixer.music.set_volume(saved_volume / 100.0)
            self._pygame_inited = True

    def play_song(self, song_id: str, song_ids: list = None) -> dict:
        try:
            self._init_player()
            self.library.reload_tracks()
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT ruta_local, titulo FROM canciones WHERE id_cancion = ?",
                    (int(song_id),),
                )
                row = cur.fetchone()
                if not row or not row["ruta_local"]:
                    return {"ok": False, "error": "Cancion no encontrada en disco"}
                song_path = row["ruta_local"]
                if not os.path.exists(song_path):
                    filename = os.path.basename(song_path)
                    alt_path = os.path.join(self._music_dir, filename)
                    if os.path.exists(alt_path):
                        song_path = os.path.normpath(alt_path)
                        cur.execute(
                            "UPDATE canciones SET ruta_local = ? WHERE id_cancion = ?",
                            (song_path, int(song_id)),
                        )

                if song_ids and len(song_ids) > 0:
                    queue_paths = []
                    queue_ids = []
                    start_index = 0
                    for sid in song_ids:
                        sid_int = int(sid)
                        cur.execute(
                            "SELECT ruta_local FROM canciones WHERE id_cancion = ?",
                            (sid_int,),
                        )
                        row2 = cur.fetchone()
                        if row2 and row2["ruta_local"]:
                            p = row2["ruta_local"]
                            if not os.path.exists(p):
                                fn = os.path.basename(p)
                                alt = os.path.join(self._music_dir, fn)
                                if os.path.exists(alt):
                                    p = os.path.normpath(alt)
                            p = os.path.normpath(os.path.abspath(p))
                            queue_paths.append(p)
                            queue_ids.append(sid_int)
                            if sid == song_id:
                                start_index = len(queue_paths) - 1
                    with self._player_lock:
                        self._music_controller.set_queue(
                            queue_paths, queue_ids, start_index
                        )
                        ok = self._music_controller.play_from_queue()
                        if not ok:
                            return {"ok": False, "error": "No se pudo reproducir desde la cola"}
                else:
                    with self._player_lock:
                        ok = self._music_controller.play_file(song_path)
                    if not ok:
                        return {"ok": False, "error": f"No se pudo reproducir: {song_path}"}

                self._current_song_id = song_id
                cur.execute(
                    "INSERT INTO historial_reproduccion (id_usuario, id_cancion) VALUES (?, ?)",
                    (1, int(song_id)),
                )
                conn.commit()
                return {
                    "ok": True,
                    "data": {
                        "message": f"Reproduciendo: {os.path.basename(song_path)}"
                    },
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def pause_song(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": False, "error": "Reproductor no inicializado"}
            with self._player_lock:
                self._music_controller.pause()
            return {"ok": True, "data": {"message": "Pausado"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def resume_song(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": False, "error": "Reproductor no inicializado"}
            with self._player_lock:
                self._music_controller.resume()
            return {"ok": True, "data": {"message": "Reanudado"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop_song(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": False, "error": "Reproductor no inicializado"}
            with self._player_lock:
                self._music_controller.stop()
            return {"ok": True, "data": {"message": "Detenido"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def seek_song(self, position: float) -> dict:
        try:
            if not self._pygame_inited or self._current_song_id is None:
                return {"ok": False, "error": "No hay canción reproduciendo"}
            with self._player_lock:
                ok = self._music_controller.seek(max(0, position))
            if not ok:
                return {"ok": False, "error": "No se pudo cambiar la posición"}
            return {"ok": True, "data": {"message": "Posición cambiada"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _sync_current_song_from_player(self):
        try:
            if self._music_controller.has_queue():
                idx = self._music_controller._queue_index
                ids = self._music_controller._queue_ids
                if 0 <= idx < len(ids):
                    song_id = ids[idx]
                    self._current_song_id = str(song_id)
                    conn = self.db.get_connection()
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO historial_reproduccion (id_usuario, id_cancion) VALUES (?, ?)",
                            (1, song_id),
                        )
                        conn.commit()
                    finally:
                        conn.close()
                    return

            idx = self._music_controller.current_index
            if 0 <= idx < len(self.library.tracks):
                track_path = os.path.normpath(self.library.tracks[idx])
                conn = self.db.get_connection()
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT id_cancion FROM canciones WHERE ruta_local = ?",
                        (track_path,),
                    )
                    row = cur.fetchone()
                    if row:
                        self._current_song_id = str(row["id_cancion"])
                        cur.execute(
                            "INSERT INTO historial_reproduccion (id_usuario, id_cancion) VALUES (?, ?)",
                            (1, row["id_cancion"]),
                        )
                        conn.commit()
                finally:
                    conn.close()
        except Exception:
            pass

    def next_song(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                self._music_controller.next_track()
            self._sync_current_song_from_player()
            return {"ok": True, "data": {"message": "Siguiente cancion"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def prev_song(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                self._music_controller.previous_track()
            self._sync_current_song_from_player()
            return {"ok": True, "data": {"message": "Cancion anterior"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def toggle_shuffle(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                enabled = self._music_controller.toggle_shuffle()
            return {"ok": True, "data": {"shuffle": enabled}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def cycle_repeat(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                mode = self._music_controller.cycle_repeat_mode()
            return {"ok": True, "data": {"repeat": mode}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # -- Now Playing / Position / Volume -----------------------

    def get_now_playing(self) -> dict:
        try:
            if not self._pygame_inited or not self._music_controller or self._current_song_id is None:
                return {"ok": True, "data": None}
            import pygame
            is_playing = pygame.mixer.music.get_busy()
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """SELECT id_cancion, titulo, artista, album, duracion_seg,
                              genero, plataforma_origen, ruta_local, caratula_url
                       FROM canciones WHERE id_cancion = ?""",
                    (int(self._current_song_id),),
                )
                row = cur.fetchone()
                if not row:
                    return {"ok": True, "data": None}
                pos = self._music_controller.get_absolute_position()
                cover = row["caratula_url"] or ""
                if not cover:
                    cover = self._ensure_cover(row["id_cancion"], row["titulo"], row["artista"] or "", row["album"] or "", row["ruta_local"] or "", row["plataforma_origen"] or "")
                cover = self._localize_cover(row["id_cancion"], cover)
                return {
                    "ok": True,
                    "data": {
                        "id": str(row["id_cancion"]),
                        "title": row["titulo"],
                        "artist": row["artista"] or "",
                        "album": row["album"] or "",
                        "duration": row["duracion_seg"] or 0,
                        "cover_url": cover,
                        "is_playing": bool(is_playing),
                        "position": pos,
                        "shuffle": self._music_controller.get_shuffle_enabled(),
                        "repeat": self._music_controller.get_repeat_mode(),
                    },
                }
            finally:
                conn.close()
        except Exception:
            return {"ok": True, "data": None}

    def get_playback_position(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": True, "data": {"position": 0.0, "is_playing": False}}
            with self._player_lock:
                import pygame
                pos = self._music_controller.get_absolute_position()
                busy = bool(pygame.mixer.music.get_busy())
                return {"ok": True, "data": {"position": max(0.0, pos), "is_playing": busy}}
        except Exception:
            return {"ok": True, "data": {"position": 0.0, "is_playing": False}}

    def set_volume(self, volume: int) -> dict:
        try:
            v = max(0, min(100, int(volume)))
            if self._pygame_inited:
                import pygame
                pygame.mixer.music.set_volume(v / 100.0)
            settings = self.get_settings()
            settings["volume"] = v
            self.update_settings({"volume": v})
            return {"ok": True, "data": {"volume": v}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_volume(self) -> dict:
        try:
            settings = self.get_settings()
            return {"ok": True, "data": {"volume": settings.get("volume", 100)}}
        except Exception:
            return {"ok": True, "data": {"volume": 100}}

    def get_recently_played(self, limit: int = 10) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                              c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url
                       FROM historial_reproduccion h
                       JOIN canciones c ON h.id_cancion = c.id_cancion
                       WHERE h.id_usuario = 1
                       GROUP BY c.id_cancion
                       ORDER BY MAX(h.fecha_reproduccion) DESC
                       LIMIT ?""",
                    (limit,),
                )
                rows = cur.fetchall()
                result = []
                for row in rows:
                    sid = row["id_cancion"]
                    cover = row["caratula_url"] or ""
                    if not cover:
                        cover = self._ensure_cover(sid, row["titulo"], row["artista"] or "", row["album"] or "", row["ruta_local"] or "", row["plataforma_origen"] or "")
                    cover = self._localize_cover(sid, cover)
                    result.append({
                        "id": str(sid),
                        "title": row["titulo"],
                        "artist": row["artista"] or "",
                        "album": row["album"] or "",
                        "duration": row["duracion_seg"] or 0,
                        "genre": row["genero"] or "",
                        "source": row["plataforma_origen"] or "",
                        "path": row["ruta_local"] or "",
                        "cover_url": cover,
                    })
                return result
            finally:
                conn.close()
        except Exception:
            return []

    def _apply_settings(self):
        """Aplica la configuración guardada a las rutas internas."""
        try:
            settings = self._load_settings()
            if "download_path" in settings:
                path = settings["download_path"]
                if os.path.isdir(path) or self._ensure_dir(path):
                    self._music_dir = path
                    self.library.music_folder = path
        except Exception:
            pass

    def _ensure_dir(self, path: str) -> bool:
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False

    def _load_settings(self) -> dict:
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                pass
        return {"volume": 100, "download_quality": "192"}

    def get_settings(self) -> dict:
        try:
            settings = self._load_settings()
            settings["download_path"] = self._music_dir
            return settings
        except Exception:
            return {"volume": 100, "download_quality": "192", "download_path": self._music_dir}

    def update_settings(self, data: dict) -> dict:
        try:
            settings = self._load_settings()
            settings.update(data)
            if "download_path" in data:
                new_path = data["download_path"]
                os.makedirs(new_path, exist_ok=True)
                self._music_dir = new_path
                self.library = MusicLibrary(self._music_dir)
            os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return {"ok": True, "data": settings}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def select_folder_dialog(self) -> dict:
        try:
            import tkinter.filedialog, tkinter
            root = tkinter.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            folder = tkinter.filedialog.askdirectory()
            root.destroy()
            if folder:
                return {"ok": True, "data": {"path": folder}}
            return {"ok": False, "error": "No se seleccionó carpeta"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # -- System Status ------------------------------------------

    def get_system_status(self) -> dict:
        deps = {}
        for name in [
            "spotdl",
            "yt_dlp",
            "moviepy",
            "mutagen",
            "requests",
            "pytubefix",
            "pygame",
        ]:
            try:
                __import__(name)
                deps[name] = True
            except ImportError:
                deps[name] = False
        ffmpeg = False
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ffmpeg = result.returncode == 0
        except Exception:
            ffmpeg = False
        return {
            "dependencies": deps,
            "ffmpeg": ffmpeg,
            "music_count": len(self.library.tracks),
        }

    def open_spotify_login(self) -> dict:
        """Open the system browser to the local spotify login endpoint.

        Returns a small dict with success status so the frontend can react.
        """
        try:
            import webbrowser
            host = "127.0.0.1"
            port = 57291
            url = f"http://{host}:{port}/spotify/login"
            webbrowser.open(url, new=2)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}
