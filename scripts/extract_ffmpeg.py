import sys
import os
import shutil
import urllib.request
import zipfile

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dst_dir = os.path.join(project_root, "assets", "ffmpeg")
os.makedirs(dst_dir, exist_ok=True)

ffmpeg_dst = os.path.join(dst_dir, "ffmpeg.exe")
ffprobe_dst = os.path.join(dst_dir, "ffprobe.exe")

# If both already exist, skip
if os.path.isfile(ffmpeg_dst) and os.path.isfile(ffprobe_dst):
    print(f"ffmpeg y ffprobe ya existen en {dst_dir}")
    sys.exit(0)

# ---------- 1. Extraer ffmpeg.exe desde imageio_ffmpeg ----------
src = None
try:
    import imageio_ffmpeg
    src = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    pass

if src and os.path.isfile(src):
    shutil.copy2(src, ffmpeg_dst)
    print(f"ffmpeg.exe extraido desde imageio_ffmpeg ({os.path.getsize(ffmpeg_dst)} bytes)")
else:
    print("ERROR: No se pudo obtener ffmpeg desde imageio_ffmpeg")
    sys.exit(1)

# ---------- 2. Descargar ffprobe.exe desde gyan.dev ----------
# Use same version as imageio_ffmpeg 0.6.0
FFMPEG_VERSION = "7.1"
ZIP_URL = f"https://github.com/GyanD/codexffmpeg/releases/download/{FFMPEG_VERSION}/ffmpeg-{FFMPEG_VERSION}-essentials_build.zip"

# Cache the zip to avoid re-downloading on every build
cache_dir = os.path.join(project_root, "assets", "ffmpeg", ".cache")
os.makedirs(cache_dir, exist_ok=True)
zip_cache = os.path.join(cache_dir, "ffmpeg-7.1-essentials_build.zip")

if not os.path.isfile(zip_cache):
    print(f"Descargando ffprobe desde {ZIP_URL} ...")
    urllib.request.urlretrieve(ZIP_URL, zip_cache)
    print("Descarga completada")
else:
    print(f"Usando cache: {zip_cache}")

try:
    with zipfile.ZipFile(zip_cache, "r") as zf:
        for name in zf.namelist():
            if name.endswith("/bin/ffprobe.exe"):
                with zf.open(name) as src_file:
                    with open(ffprobe_dst, "wb") as dst_file:
                        shutil.copyfileobj(src_file, dst_file)
                print(f"ffprobe.exe extraido ({os.path.getsize(ffprobe_dst)} bytes)")
                break
        else:
            print("ERROR: No se encontro ffprobe.exe dentro del zip")
            sys.exit(1)
except Exception as e:
    print(f"ERROR extrayendo ffprobe del zip: {e}")
    sys.exit(1)

print(f"Listo: ffmpeg.exe y ffprobe.exe en {dst_dir}")
