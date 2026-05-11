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

def main():
    _check_web_dir()
    print(f"Iniciando servidor estatico en {URL}...")
    server = serve(port=PORT)
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
    webview.start(debug=True)
    print("Cerrando servidor...")
    server.shutdown()


if __name__ == "__main__":
    main()
