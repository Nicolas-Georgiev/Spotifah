import os
import sys
import json
import threading
import time

_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    from model.spotify2mp3_model import Spotify2MP3Converter
    from model.youtube2mp3_model import YouTube2MP3Converter
    from model.soundcloud2mp3 import SoundCloudConverter
    from controller.music_controller import MusicController
    from model.music_library import MusicLibrary
    from databaseManager.db import Database

from api.converters import ConvertersMixin
from api.playlists import PlaylistsMixin
from api.player import PlayerMixin
from api.covers import CoversMixin
from api.recommendations import RecommendationsMixin
from api.settings import SettingsMixin
from api.system import SystemMixin
from api.local_import import LocalImportMixin


class Api(ConvertersMixin, PlaylistsMixin, PlayerMixin, CoversMixin, RecommendationsMixin, SettingsMixin, SystemMixin, LocalImportMixin):
    def __init__(self):
        self._project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

        self._apply_settings()
        self._sync_local_music_library()

        self._music_controller = None
        self._pygame_inited = False
        self._player_lock = threading.Lock()

        self._ensure_system_playlists()

        self._current_song_id = None

        self._import_tasks: dict[str, dict] = {}
        self._import_counter = 0
        self._recommendation_engine = None
        self._recommendation_signature = None

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
        target = os.path.join(self._bdd_dir, "ekho.db")
        if os.path.exists(target):
            return
        seed = os.path.join(self._project_root, "data", "BDD", "ekho.db")
        if os.path.exists(seed):
            import shutil
            shutil.copy2(seed, target)

    def _sync_local_music_library(self):
        try:
            import contextlib
            import io
            from model.db_adapter import upsert_cancion_json
        except Exception:
            return

        if not os.path.isdir(self._music_dir):
            return

        db_path = self.db.db_path if hasattr(self.db, "db_path") else None
        supported_extensions = {".mp3"}

        for entry in os.scandir(self._music_dir):
            if not entry.is_file():
                continue
            if os.path.splitext(entry.name)[1].lower() not in supported_extensions:
                continue

            try:
                metadata = self._extract_metadata(entry.path)
            except Exception:
                metadata = {"titulo": os.path.splitext(entry.name)[0]}

            metadata.update({
                "ruta_local": entry.path,
                "plataforma_origen": "local",
            })
            with contextlib.redirect_stdout(io.StringIO()):
                upsert_cancion_json(metadata, db_path=db_path)

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

    def _ensure_favorites_playlist(self):
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id_playlist FROM playlists WHERE nombre = ? AND id_usuario = ?",
                    ("Favoritos", 1),
                )
                row = cur.fetchone()
                if row:
                    return row["id_playlist"]
                cur.execute(
                    "INSERT INTO playlists (id_usuario, nombre, descripcion, publica) VALUES (?, ?, ?, ?)",
                    (1, "Favoritos", "Tus canciones favoritas", 0),
                )
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()
        except Exception:
            return None
