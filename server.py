import json
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

    @staticmethod
    def _get_portadas_dir():
        base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).parent
        return str(base / "assets" / "portadas")

    def do_GET(self):
        path = self.path.split("?")[0]
        if path.startswith("/api/covers/"):
            return self._serve_cover(path)
        if path.startswith("/api/playlist-covers/"):
            return self._serve_playlist_cover(path)
        if path.startswith("/portadas/"):
            return self._serve_portada(path)
        if path.startswith("/assets/") or path == "/favicon.ico":
            return super().do_GET()
        if path == "/index.html":
            return self._serve_index_html()
        web_dir = self._get_web_dir()
        file_path = path.lstrip("/")
        full_path = os.path.join(web_dir, file_path)
        if os.path.isfile(full_path):
            return super().do_GET()
        return self._serve_index_html()

    def _serve_blob_from_db(self, table: str, id_column: str, id_value, ctype: str):
        db_path = os.path.join(self.data_dir, "BDD", "ekho.db") if self.data_dir else None
        if not db_path or not os.path.isfile(db_path):
            self.send_response(404)
            self.end_headers()
            return False
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            try:
                cur = conn.cursor()
                cur.execute(
                    f"SELECT caratula_blob FROM {table} WHERE {id_column} = ?",
                    (int(id_value),),
                )
                row = cur.fetchone()
                if row and row["caratula_blob"]:
                    blob = row["caratula_blob"]
                    self.send_response(200)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(len(blob)))
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.end_headers()
                    self.wfile.write(blob)
                    return True
            finally:
                conn.close()
        except Exception:
            pass
        return False

    def _serve_image_from_disk(self, path: str, ctype: str) -> bool:
        if os.path.isfile(path):
            try:
                with open(path, "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(data)
                return True
            except Exception:
                pass
        return False

    def _serve_cover(self, path):
        filename = path.split("/api/covers/")[-1]
        if not filename or ".." in filename or "/" in filename:
            self.send_response(404)
            self.end_headers()
            return
        parts = filename.rsplit(".", 1)
        if len(parts) != 2:
            self.send_response(404)
            self.end_headers()
            return
        song_id_str, ext = parts
        ctype = mimetypes.guess_type(f"x.{ext}")[0] or "image/jpeg"

        if song_id_str.startswith("preview_"):
            covers_dir = os.path.join(self.data_dir, "covers") if self.data_dir else None
            if covers_dir:
                filepath = os.path.join(covers_dir, filename)
                if self._serve_image_from_disk(filepath, ctype):
                    return
            self.send_response(404)
            self.end_headers()
            return

        if not self._serve_blob_from_db("canciones", "id_cancion", song_id_str, ctype):
            self.send_response(404)
            self.end_headers()

    def _serve_playlist_cover(self, path):
        filename = path.split("/api/playlist-covers/")[-1]
        if not filename or ".." in filename or "/" in filename:
            self.send_response(404)
            self.end_headers()
            return
        parts = filename.rsplit(".", 1)
        if len(parts) != 2:
            self.send_response(404)
            self.end_headers()
            return
        playlist_id_str, ext = parts
        ctype = mimetypes.guess_type(f"x.{ext}")[0] or "image/jpeg"

        if not self._serve_blob_from_db("playlists", "id_playlist", playlist_id_str, ctype):
            self.send_response(404)
            self.end_headers()

    def _serve_portada(self, path):
        filename = path.split("/portadas/")[-1]
        if not filename or ".." in filename or "/" in filename:
            self.send_response(404)
            self.end_headers()
            return
        portadas_dir = self._get_portadas_dir()
        filepath = os.path.join(portadas_dir, filename)
        if not os.path.isfile(filepath):
            self.send_response(404)
            self.end_headers()
            return
        ctype = mimetypes.guess_type(filename)[0] or "image/svg+xml"
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "max-age=86400")
            self.end_headers()
            self.wfile.write(data)
        except Exception:
            self.send_response(404)
            self.end_headers()

    def _serve_index_html(self):
        web_dir = self._get_web_dir()
        index_path = os.path.join(web_dir, "index.html")
        if not os.path.isfile(index_path):
            self.send_response(404)
            self.end_headers()
            return

        theme = "default"
        if self.data_dir:
            settings_path = os.path.join(self.data_dir, "settings.json")
            if os.path.isfile(settings_path):
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                    t = settings.get("theme")
                    if t in ("default", "dark", "light"):
                        theme = t
                except Exception:
                    pass

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("__INITIAL_THEME__", theme)

            body = content.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.send_response(500)
            self.end_headers()

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
