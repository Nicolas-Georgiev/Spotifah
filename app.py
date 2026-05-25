import os
import sys
import time
import urllib.request
import webview
from api import Api
from server import serve

PORT = 57291
URL = f"http://127.0.0.1:{PORT}"

def _check_web_dir():
    if getattr(sys, "frozen", False):
        web = os.path.join(sys._MEIPASS, "web")
    else:
        web = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
    if not os.path.isfile(os.path.join(web, "index.html")):
        print(f"ERROR: No se encuentra web/index.html en {web}")
        print("Ejecuta primero: cd lovable-code && npm run build")
        sys.exit(1)

def _wait_for_server(url, timeout=10):
    for _ in range(timeout):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(0.5)
    return False

def _resolve_data_dir():
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif sys.platform == "darwin":
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        else:
            base = os.path.join(os.path.expanduser("~"), ".local", "share")
        return os.path.join(base, "EKHO", "data")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def _set_ffmpeg_env():
    if not getattr(sys, 'frozen', False):
        return
    ffmpeg = os.path.join(
        sys._MEIPASS,
        'imageio_ffmpeg', 'binaries',
        'ffmpeg-win-x86_64-v7.1.exe'
    )
    if os.path.isfile(ffmpeg):
        os.environ['IMAGEIO_FFMPEG_EXE'] = ffmpeg
        os.environ['EKHO_FFMPEG_PATH'] = ffmpeg

def main():
    _check_web_dir()
    _set_ffmpeg_env()
    data_dir = _resolve_data_dir()
    print(f"Iniciando servidor estatico en {URL}...")
    server = serve(port=PORT, data_dir=data_dir)
    if not _wait_for_server(URL):
        print("ERROR: El servidor no respondio a tiempo")
        server.shutdown()
        sys.exit(1)
    print("Servidor listo. Abriendo EKHO...")
    api = Api()
    window = webview.create_window(
        "EKHO",
        URL,
        js_api=api,
        width=1280,
        height=800,
        min_size=(960, 600),
    )
    webview.start()
    print("Cerrando servidor...")
    server.shutdown()


if __name__ == "__main__":
    main()
