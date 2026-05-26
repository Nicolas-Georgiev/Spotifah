import os
import io
import time
import threading
import contextlib

import sys
_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from api.covers import CoversMixin


class ConvertersMixin(CoversMixin):
    def convert_youtube(self, url: str) -> dict:
        ok, msg = self._check_ffmpeg()
        if not ok:
            return {"ok": False, "error": msg}
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                from model.youtube2mp3_model import YouTube2MP3Converter
                converter = YouTube2MP3Converter()
                converter.set_download_folder(self._music_dir)
                result_path = converter.convert(url)
            if hasattr(self, "_sync_local_music_library"):
                self._sync_local_music_library()
            if hasattr(self, "library") and self.library is not None:
                self.library.reload_tracks()
            return {
                "ok": True,
                "data": {
                    "path": result_path,
                    "filename": os.path.basename(result_path),
                    "log": f.getvalue(),
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "log": f.getvalue()}

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
                from model.spotify2mp3_model import Spotify2MP3Converter
                converter = Spotify2MP3Converter()
                converter.set_download_folder(self._music_dir)
                result_path = converter.convert(url)
            if hasattr(self, "_sync_local_music_library"):
                self._sync_local_music_library()
            if hasattr(self, "library") and self.library is not None:
                self.library.reload_tracks()
            return {
                "ok": True,
                "data": {
                    "path": result_path,
                    "filename": os.path.basename(result_path),
                    "log": f.getvalue(),
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "log": f.getvalue()}

    def convert_soundcloud(self, url: str) -> dict:
        ok, msg = self._check_ffmpeg()
        if not ok:
            return {"ok": False, "error": msg}
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                from model.soundcloud2mp3 import SoundCloudConverter
                converter = SoundCloudConverter(self._music_dir)
                result_path = converter.convert(url)
            if result_path is None:
                return {"ok": False, "error": "La conversión falló", "log": f.getvalue()}
            if hasattr(self, "_sync_local_music_library"):
                self._sync_local_music_library()
            if hasattr(self, "library") and self.library is not None:
                self.library.reload_tracks()
            return {
                "ok": True,
                "data": {
                    "path": result_path,
                    "filename": os.path.basename(result_path),
                    "log": f.getvalue(),
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e), "log": f.getvalue()}

    # ── Album Preview ────────────────────────────────────────────

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
        from model.soundcloud2mp3 import SoundCloudConverter

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

    # ── Playlist Import ──────────────────────────────────────────

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
            return {"ok": False, "error": "La URL no corresponde a una playlist válida"}

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
                        from model.spotify2mp3_model import Spotify2MP3Converter
                        converter = Spotify2MP3Converter()
                        self._import_spotify_playlist(task, converter, url)
                    elif detection["platform"] == "youtube":
                        from model.youtube2mp3_model import YouTube2MP3Converter
                        converter = YouTube2MP3Converter()
                        self._import_youtube_playlist(task, converter, url)
                    elif detection["platform"] == "soundcloud":
                        from model.soundcloud2mp3 import SoundCloudConverter
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
        print(f"Obteniendo {total} vídeos de: {task['playlist_name']}")

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

        self._finalize_import(task, song_ids, cover_url, url, "SoundCloud")

    def _finalize_import(self, task: dict, song_ids: list, cover_url: str, url: str, platform_name: str):
        if not song_ids:
            task["status"] = "error"
            task["error"] = "No se pudo importar ninguna canción"
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
