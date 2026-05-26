"""
frozen_utils.py
Utilidades de resolución de rutas para modo frozen (PyInstaller --onedir).

En modo desarrollo las rutas se calculan desde __file__.
En modo frozen (exe) PyInstaller aplana src/model/ → model/, src/databaseManager/ → databaseManager/,
por lo que las rutas relativas con múltiples ".." quedan incorrectas.
Este módulo centraliza la lógica para obtener siempre la ruta correcta.
"""

import os
import sys
import glob
import shutil


def get_app_root() -> str:
    """
    Devuelve la raíz de la aplicación:
    - Frozen (exe): sys._MEIPASS  (= carpeta del exe con --onedir)
    - Desarrollo:   raíz del proyecto (padre de src/)
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    # En desarrollo: este archivo está en src/, sube un nivel
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_dir() -> str:
    """
    Devuelve el directorio de datos del usuario:
    - Frozen: %AppData%/EKHO/data  (Windows)
    - Desarrollo: <project_root>/data
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif sys.platform == "darwin":
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        else:
            base = os.path.join(os.path.expanduser("~"), ".local", "share")
        return os.path.join(base, "EKHO", "data")
    return os.path.join(get_app_root(), "data")


def get_music_dir() -> str:
    return os.path.join(get_data_dir(), "music")


def get_db_path() -> str:
    return os.path.join(get_data_dir(), "BDD", "ekho.db")


def get_dotenv_path() -> str:
    return os.path.join(get_app_root(), ".env")


def _candidate_ffmpeg_dirs() -> list[str]:
    dirs: list[str] = []

    env = os.environ.get("EKHO_FFMPEG_PATH") or os.environ.get("IMAGEIO_FFMPEG_EXE")
    if env:
        dirs.append(env if os.path.isdir(env) else os.path.dirname(env))

    for command in ("ffmpeg", "ffmpeg.exe"):
        found = shutil.which(command)
        if found:
            dirs.append(os.path.dirname(found))

    if getattr(sys, "frozen", False):
        dirs.append(os.path.join(sys._MEIPASS, "imageio_ffmpeg", "binaries"))

    try:
        import imageio_ffmpeg

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe:
            dirs.append(os.path.dirname(exe))
    except Exception:
        pass

    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        program_files = os.environ.get("ProgramFiles")
        program_files_x86 = os.environ.get("ProgramFiles(x86)")
        patterns = []
        if local:
            patterns.append(os.path.join(local, "Microsoft", "WinGet", "Packages", "*FFmpeg*", "*", "bin"))
        if program_files:
            patterns.append(os.path.join(program_files, "*ffmpeg*", "bin"))
            patterns.append(os.path.join(program_files, "ffmpeg", "bin"))
        if program_files_x86:
            patterns.append(os.path.join(program_files_x86, "*ffmpeg*", "bin"))
        for pattern in patterns:
            dirs.extend(glob.glob(pattern))

    unique_dirs = []
    seen = set()
    for directory in dirs:
        if not directory:
            continue
        normalized = os.path.abspath(directory)
        if normalized not in seen and os.path.isdir(normalized):
            seen.add(normalized)
            unique_dirs.append(normalized)
    return unique_dirs


def resolve_ffmpeg_exe() -> str:
    exe_names = ("ffmpeg.exe", "ffmpeg") if sys.platform == "win32" else ("ffmpeg",)
    for directory in _candidate_ffmpeg_dirs():
        for name in exe_names:
            candidate = os.path.join(directory, name)
            if os.path.isfile(candidate):
                return candidate
    return shutil.which("ffmpeg") or "ffmpeg"


def resolve_ffprobe_exe() -> str:
    exe_names = ("ffprobe.exe", "ffprobe") if sys.platform == "win32" else ("ffprobe",)
    for directory in _candidate_ffmpeg_dirs():
        for name in exe_names:
            candidate = os.path.join(directory, name)
            if os.path.isfile(candidate):
                return candidate
    return shutil.which("ffprobe") or "ffprobe"


def resolve_ytdlp_ffmpeg_location() -> str:
    for directory in _candidate_ffmpeg_dirs():
        ffmpeg = os.path.join(directory, "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        ffprobe = os.path.join(directory, "ffprobe.exe" if sys.platform == "win32" else "ffprobe")
        if os.path.isfile(ffmpeg) and os.path.isfile(ffprobe):
            return directory
    return os.path.dirname(resolve_ffmpeg_exe()) or resolve_ffmpeg_exe()


def configure_ffmpeg_env() -> str:
    ffmpeg = resolve_ffmpeg_exe()
    ffmpeg_dir = os.path.dirname(ffmpeg)
    if ffmpeg_dir and os.path.isdir(ffmpeg_dir):
        path_parts = os.environ.get("PATH", "").split(os.pathsep)
        if ffmpeg_dir not in path_parts:
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
    os.environ["EKHO_FFMPEG_PATH"] = ffmpeg
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg
    return ffmpeg
