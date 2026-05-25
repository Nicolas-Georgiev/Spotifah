import os
import sys
import subprocess


class SystemMixin:
    def _get_ffmpeg_path(self) -> str:
        env = os.environ.get('EKHO_FFMPEG_PATH')
        if env:
            return env
        if getattr(sys, 'frozen', False):
            bundled = os.path.join(
                sys._MEIPASS,
                'imageio_ffmpeg', 'binaries',
                'ffmpeg-win-x86_64-v7.1.exe'
            )
            if os.path.exists(bundled):
                return bundled
        return 'ffmpeg'

    def _check_ffmpeg(self) -> tuple[bool, str]:
        ffmpeg = self._get_ffmpeg_path()
        try:
            result = subprocess.run(
                [ffmpeg, "-version"],
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
        ffmpeg = False
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
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
