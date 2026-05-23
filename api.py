import os
import sys
import json
import threading
import subprocess

_src_dir = os.path.join(os.path.dirname(__file__), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    from model.spotify2mp3_model import Spotify2MP3Converter
    from model.youtube2mp3_model import YouTube2MP3Converter
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

        self._music_controller = None
        self._pygame_inited = False
        self._player_lock = threading.Lock()

        threading.Thread(target=self._ensure_system_playlists, daemon=True).start()

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

    # ── Cover extraction & local caching ────────────────────────

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
            local_path = os.path.join(self._covers_dir, f"{song_id}.{ext}")
            if not os.path.exists(local_path):
                import urllib.request
                urllib.request.urlretrieve(external_url, local_path)
            local_url = f"/api/covers/{song_id}.{ext}"
            self._save_cover_to_db(song_id, local_url)
            return local_url
        except Exception:
            return external_url

    def _save_cover_to_db(self, song_id: int, cover_url: str):
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE canciones SET caratula_url = ? WHERE id_cancion = ?",
                    (cover_url, song_id),
                )
                conn.commit()
            finally:
                conn.close()
        except Exception:
            pass

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
                            cover_path = os.path.join(self._covers_dir, f"{song_id}.{ext}")
                            with open(cover_path, "wb") as f:
                                f.write(tag.data)
                            local_url = f"/api/covers/{song_id}.{ext}"
                            self._save_cover_to_db(song_id, local_url)
                            return local_url
            except Exception:
                pass

        return ""

    # ── YouTube → MP3 ──────────────────────────────────────────

    def convert_youtube(self, url: str) -> dict:
        try:
            f = io.StringIO()
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                converter = YouTube2MP3Converter()
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
            return {"ok": False, "error": str(e)}

    # ── Spotify → MP3 ─────────────────────────────────────────

    def convert_spotify(self, url: str) -> dict:
        try:
            f = io.StringIO()
            with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
                converter = Spotify2MP3Converter()
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
            return {"ok": False, "error": str(e)}

    # ── Playlists ──────────────────────────────────────────────

    def get_playlists(self) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id_playlist, nombre, descripcion, publica FROM playlists ORDER BY id_playlist"
                )
                playlists = [
                    {
                        "id": str(row["id_playlist"]),
                        "name": row["nombre"],
                        "description": row["descripcion"] or "",
                        "is_public": bool(row["publica"]),
                    }
                    for row in cur.fetchall()
                ]
                playlists.insert(
                    0,
                    {
                        "id": "all",
                        "name": "Todas mis canciones",
                        "description": "Todas las canciones en tu biblioteca",
                        "is_public": False,
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
                }
            ]

    def get_playlist_songs(self, playlist_id: str) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                if playlist_id == "all":
                    cur.execute(
                        """SELECT id_cancion, titulo, artista, album, duracion_seg,
                                  genero, plataforma_origen, ruta_local, caratula_url
                           FROM canciones ORDER BY titulo"""
                    )
                else:
                    cur.execute(
                        """SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                                  c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url
                           FROM playlist_canciones pc
                           JOIN canciones c ON pc.id_cancion = c.id_cancion
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
                    "SELECT COALESCE(MAX(orden), 0) + 1 FROM playlist_canciones WHERE id_playlist = ?",
                    (int(playlist_id),),
                )
                next_order = cur.fetchone()[0]
                cur.execute(
                    "INSERT OR IGNORE INTO playlist_canciones (id_playlist, id_cancion, orden) VALUES (?, ?, ?)",
                    (int(playlist_id), int(song_id), next_order),
                )
                conn.commit()
                return {"ok": True, "data": {"message": "Cancion anadida a la playlist"}}
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

    # ── Playback ───────────────────────────────────────────────

    def _init_player(self):
        if not self._pygame_inited:
            import pygame

            pygame.mixer.init()
            self.library = MusicLibrary(self._music_dir)
            self._music_controller = MusicController(self.library)
            self._pygame_inited = True

    def play_song(self, song_id: str) -> dict:
        try:
            self._init_player()
            self.library.reload_tracks()
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT ruta_local FROM canciones WHERE id_cancion = ?",
                    (int(song_id),),
                )
                row = cur.fetchone()
                if not row or not row["ruta_local"]:
                    return {"ok": False, "error": "Cancion no encontrada en disco"}
                song_path = row["ruta_local"]
                for i, t in enumerate(self.library.tracks):
                    if os.path.normpath(t) == os.path.normpath(song_path):
                        self._music_controller.current_index = i
                        break
                with self._player_lock:
                    self._music_controller.play()
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

    def next_song(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                self._music_controller.next_track()
            return {"ok": True, "data": {"message": "Siguiente cancion"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def prev_song(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                self._music_controller.previous_track()
            return {"ok": True, "data": {"message": "Cancion anterior"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Settings ───────────────────────────────────────────────

    def get_settings(self) -> dict:
        try:
            if os.path.exists(self._settings_file):
                with open(self._settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {"volume": 80, "theme": "dark", "download_quality": "192"}
        except Exception:
            return {"volume": 80, "theme": "dark", "download_quality": "192"}

    def update_settings(self, data: dict) -> dict:
        try:
            settings = self.get_settings()
            settings.update(data)
            os.makedirs(os.path.dirname(self._settings_file), exist_ok=True)
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return {"ok": True, "data": settings}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── System Status ──────────────────────────────────────────

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
