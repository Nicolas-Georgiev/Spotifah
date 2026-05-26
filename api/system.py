import os
import subprocess

from frozen_utils import configure_ffmpeg_env, resolve_ffmpeg_exe, resolve_ffprobe_exe

import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    from model.music_library import MusicLibrary

class SystemMixin:
    def delete_all_data(self) -> dict:
        try:
            if self._pygame_inited and self._music_controller:
                with self._player_lock:
                    try:
                        import pygame
                        pygame.mixer.music.stop()
                        pygame.mixer.quit()
                    except Exception:
                        pass
            self._current_song_id = None
            self._pygame_inited = False
            self._music_controller = None

            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM playlist_canciones")
                cur.execute("DELETE FROM historial_reproduccion")
                cur.execute("DELETE FROM descargas")
                cur.execute("DELETE FROM playlists")
                cur.execute("DELETE FROM canciones")
                conn.commit()
            finally:
                conn.close()

            import stat as _stat
            for entry in os.listdir(self._music_dir):
                path = os.path.join(self._music_dir, entry)
                try:
                    if os.path.isfile(path):
                        os.chmod(path, _stat.S_IWRITE)
                        os.remove(path)
                except Exception:
                    pass

            for entry in os.listdir(self._covers_dir):
                path = os.path.join(self._covers_dir, entry)
                try:
                    if os.path.isfile(path):
                        os.remove(path)
                except Exception:
                    pass

            self.library = MusicLibrary(self._music_dir)
            self._ensure_system_playlists()

            return {"ok": True, "data": {"message": "Todos los datos eliminados"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}


    def _get_ffmpeg_path(self) -> str:
        try:
            configure_ffmpeg_env()
            return resolve_ffmpeg_exe()
        except Exception:
            return os.environ.get("EKHO_FFMPEG_PATH") or "ffmpeg"

    def _check_ffmpeg(self) -> tuple[bool, str]:
        ffmpeg = self._get_ffmpeg_path()
        ffprobe = resolve_ffprobe_exe()
        try:
            ffmpeg_result = subprocess.run(
                [ffmpeg, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ffprobe_result = subprocess.run(
                [ffprobe, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if ffmpeg_result.returncode == 0 and ffprobe_result.returncode == 0:
                return True, ""
            return False, "ffmpeg o ffprobe no responden correctamente"
        except FileNotFoundError:
            return False, (
                "ffmpeg/ffprobe no estan instalados. "
                "Descargalo desde https://ffmpeg.org/download.html "
                "y asegurate de que este en el PATH del sistema"
            )
        except Exception as e:
            return False, f"Error al verificar ffmpeg/ffprobe: {e}"

    def _check_spotify_creds(self) -> tuple[bool, str]:
        client_id = os.getenv("SPOTIFY_CLIENT_ID") or os.getenv("SPOTDL_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET") or os.getenv("SPOTDL_CLIENT_SECRET")
        if not client_id or not client_secret:
            try:
                dotenv_path = os.path.join(self._project_root, ".env")
                if os.path.exists(dotenv_path):
                    with open(dotenv_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("#") or "=" not in line:
                                continue
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k in ("SPOTIFY_CLIENT_ID", "SPOTDL_CLIENT_ID") and not client_id:
                                client_id = v
                            if k in ("SPOTIFY_CLIENT_SECRET", "SPOTDL_CLIENT_SECRET") and not client_secret:
                                client_secret = v
            except Exception:
                pass
        if client_id and client_secret:
            return True, ""
        return False, (
            "SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET no configurados.\n"
            "Crea un archivo .env en la raiz del proyecto con:\n"
            "SPOTIFY_CLIENT_ID=tu_client_id\n"
            "SPOTIFY_CLIENT_SECRET=tu_client_secret\n"
            "o configuralos como variables de entorno."
        )

    def get_system_status(self) -> dict:
        deps = {}
        for name in [
            "spotdl", "yt_dlp", "moviepy", "mutagen",
            "requests", "pytubefix", "pygame",
        ]:
            try:
                __import__(name)
                deps[name] = True
            except ImportError:
                deps[name] = False
        ffmpeg_path = self._get_ffmpeg_path()
        ffprobe_path = resolve_ffprobe_exe()
        ffmpeg = False
        try:
            ffmpeg_result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ffprobe_result = subprocess.run(
                [ffprobe_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            ffmpeg = ffmpeg_result.returncode == 0 and ffprobe_result.returncode == 0
        except Exception:
            ffmpeg = False
        return {
            "dependencies": deps,
            "ffmpeg": ffmpeg,
            "music_count": len(self.library.tracks),
        }
