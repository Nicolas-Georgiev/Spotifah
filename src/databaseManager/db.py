import os
import sqlite3

SCHEMA_SQL = r"""
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    contraseña_hash TEXT NOT NULL,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    pais TEXT,
    preferencias_generos TEXT,
    preferencias_artistas TEXT
);

CREATE TABLE IF NOT EXISTS canciones (
    id_cancion INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    artista TEXT,
    album TEXT,
    duracion_seg INTEGER,
    genero TEXT,
    plataforma_origen TEXT DEFAULT 'local',
    url_origen TEXT,
    ruta_local TEXT,
    caratula_url TEXT,
    caratula_blob BLOB,
    letra TEXT,
    fecha_importacion DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS playlists (
    id_playlist INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    publica INTEGER DEFAULT 0,
    playlist_json TEXT,
    caratula_blob BLOB,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS playlist_canciones (
    id_playlist INTEGER NOT NULL,
    id_cancion INTEGER NOT NULL,
    orden INTEGER DEFAULT 1,
    PRIMARY KEY (id_playlist, id_cancion),
    FOREIGN KEY (id_playlist) REFERENCES playlists(id_playlist) ON DELETE CASCADE,
    FOREIGN KEY (id_cancion) REFERENCES canciones(id_cancion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS historial_reproduccion (
    id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_cancion INTEGER NOT NULL,
    fecha_reproduccion DATETIME DEFAULT CURRENT_TIMESTAMP,
    duracion_reproducida INTEGER,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_cancion) REFERENCES canciones(id_cancion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS recomendaciones (
    id_recomendacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_cancion INTEGER NOT NULL,
    score REAL,
    fecha_generada DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_cancion) REFERENCES canciones(id_cancion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS descargas (
    id_descarga INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    id_cancion INTEGER NOT NULL,
    fecha_descarga DATETIME DEFAULT CURRENT_TIMESTAMP,
    formato TEXT DEFAULT 'mp3',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_cancion) REFERENCES canciones(id_cancion) ON DELETE CASCADE
);

INSERT OR IGNORE INTO usuarios (id_usuario, nombre_usuario, correo, contraseña_hash, pais, preferencias_generos, preferencias_artistas)
VALUES
(1,'Usuario','usuario@mail.com','hash',NULL,NULL,NULL);

INSERT OR IGNORE INTO playlists (id_playlist, id_usuario, nombre, descripcion, publica)
VALUES (1, 1, 'Favoritos', 'Tus canciones favoritas', 0);
"""

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            if getattr(sys, 'frozen', False):
                # Modo frozen (exe): usar AppData del usuario
                if sys.platform == 'win32':
                    base = os.environ.get('APPDATA', os.path.expanduser('~'))
                elif sys.platform == 'darwin':
                    base = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
                else:
                    base = os.path.join(os.path.expanduser('~'), '.local', 'share')
                db_path = os.path.join(base, 'EKHO', 'data', 'BDD', 'ekho.db')
            else:
                # Modo desarrollo: src/databaseManager -> src -> project_root -> data/BDD/ekho.db
                db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "BDD", "ekho.db")
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Si la BD no existe, la inicializa
        if not os.path.exists(self.db_path):
            self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        conn = self.get_connection()
        try:
            conn.executescript(SCHEMA_SQL)
            conn.commit()
            print(f"Base de datos creada en: {self.db_path}")
        finally:
            conn.close()