import os
import sys
import threading
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class SPAHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        mimetypes.init()
        mimetypes.add_type("application/javascript", ".js")
        mimetypes.add_type("text/javascript", ".mjs")
        super().__init__(*args, directory=self._get_web_dir(), **kwargs)

    @staticmethod
    def _get_web_dir():
        if getattr(sys, "frozen", False):
            return str(Path(sys._MEIPASS) / "web")
        return str(Path(__file__).parent / "web")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/assets/") or path == "/favicon.ico":
            return super().do_GET()
        self.path = "/index.html"
        return super().do_GET()

    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def serve(host="127.0.0.1", port=57291):
    server = HTTPServer((host, port), SPAHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


if __name__ == "__main__":
    import time
    s = serve()
    print(f"Sirviendo en http://127.0.0.1:57291")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        s.shutdown()
