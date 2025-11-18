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
(1,'Juan','juan@mail.com','hash123','España','["Pop","Rock"]','["Artista A","Artista B"]'),
(2,'Ana','ana@mail.com','hash456','México','["Jazz","Pop"]','["Artista C"]'),
(3,'Luis','luis@mail.com','hash789','Argentina','["Electrónica","Rock"]','["Artista A","Artista D"]');

INSERT OR IGNORE INTO canciones (id_cancion, titulo, artista, album, duracion_seg, genero, plataforma_origen)
VALUES
(1,'Canción 1','Artista A','Album X',210,'Pop','Spotify'),
(2,'Canción 2','Artista B','Album Y',180,'Rock','YouTube'),
(3,'Canción 3','Artista C','Album Z',240,'Jazz','SoundCloud'),
(4,'Canción 4','Artista D','Album W',300,'Electrónica','Local');

INSERT OR IGNORE INTO playlists (id_playlist, id_usuario, nombre, descripcion, publica)
VALUES
(1,1,'Mis Favoritas','Canciones que me gustan',1),
(2,2,'Jazz para la tarde','Playlist de Jazz relajante',1);

INSERT OR IGNORE INTO playlist_canciones (id_playlist, id_cancion, orden)
VALUES
(1,1,1),
(1,2,2),
(2,3,1);

INSERT OR IGNORE INTO historial_reproduccion (id_historial, id_usuario, id_cancion, duracion_reproducida)
VALUES
(1,1,1,210),
(2,1,2,180),
(3,2,3,240),
(4,3,4,300);

INSERT OR IGNORE INTO recomendaciones (id_recomendacion, id_usuario, id_cancion, score)
VALUES
(1,1,3,0.95),
(2,2,1,0.85),
(3,3,2,0.90);

INSERT OR IGNORE INTO descargas (id_descarga, id_usuario, id_cancion, formato)
VALUES
(1,1,1,'mp3'),
(2,1,2,'wav'),
(3,2,3,'mp3');
"""

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "BDD", "ekho.db")
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