import os
import sys
import threading
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


class SPAHandler(SimpleHTTPRequestHandler):
    data_dir = None

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
        if path.startswith("/api/covers/"):
            return self._serve_cover(path)
        if path.startswith("/assets/") or path == "/favicon.ico":
            return super().do_GET()
        web_dir = self._get_web_dir()
        file_path = path.lstrip("/")
        full_path = os.path.join(web_dir, file_path)
        if os.path.isfile(full_path):
            return super().do_GET()
        self.path = "/index.html"
        return super().do_GET()

    def _serve_cover(self, path):
        filename = path.split("/api/covers/")[-1]
        if not filename or ".." in filename or "/" in filename:
            self.send_response(404)
            self.end_headers()
            return
        covers_dir = os.path.join(self.data_dir, "covers") if self.data_dir else None
        if not covers_dir or not os.path.isdir(covers_dir):
            self.send_response(404)
            self.end_headers()
            return
        filepath = os.path.join(covers_dir, filename)
        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return
        ctype, _ = mimetypes.guess_type(filepath)
        self.send_response(200)
        self.send_header("Content-Type", ctype or "image/jpeg")
        self.send_header("Cache-Control", "max-age=86400")
        self.send_header("Content-Length", os.path.getsize(filepath))
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def serve(host="127.0.0.1", port=57291, data_dir=None):
    SPAHandler.data_dir = data_dir
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
