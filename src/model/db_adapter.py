# db_adapter.py
"""
Capa de acceso a la BD SQLite (ekho.db) para los conversores.
Expone upsert_cancion() y registrar_descarga() que se llaman
automáticamente al terminar cada conversión a MP3.
"""

import os
import sys

# Asegurar que 'src' esté en el path para importar databaseManager
_src_dir = os.path.dirname(os.path.dirname(__file__))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

try:
    from databaseManager.db import Database
    _DB_AVAILABLE = True
except Exception as _e:
    print(f"⚠️ db_adapter: no se pudo importar Database ({_e}). El guardado en BD estará desactivado.")
    _DB_AVAILABLE = False


def _get_db(db_path=None):
    """Devuelve una instancia de Database, creando la BD si no existe."""
    return Database(db_path)


def upsert_cancion(metadata: dict, db_path=None) -> int | None:
    """
    Inserta una canción en la tabla 'canciones' o actualiza ruta_local/caratula_url
    si ya existe (match por titulo + artista).

    Acepta tanto el formato de SpotifyInfoExtractor (claves en español)
    como el formato de YouTube2MP3Converter (claves en inglés).

    Devuelve id_cancion o None si falla.
    """
    if not _DB_AVAILABLE:
        return None

    # Normalizar claves — soportar ambos formatos de metadatos
    titulo = (metadata.get('titulo') or metadata.get('name') or
              metadata.get('title') or '').strip()
    artista = (metadata.get('artista') or metadata.get('artist') or
               metadata.get('author') or '').strip()
    album = (metadata.get('album') or '').strip()
    duracion_seg = (metadata.get('duracion_seg') or metadata.get('duration') or
                    metadata.get('length') or None)
    genero = metadata.get('genero') or None
    plataforma_origen = (metadata.get('plataforma_origen') or
                         metadata.get('source') or 'local').strip()
    url_origen = metadata.get('url_origen') or metadata.get('url') or None
    ruta_local = metadata.get('ruta_local') or None
    caratula_url = (metadata.get('caratula_url') or metadata.get('thumbnail_url') or
                    metadata.get('image_url') or None)
    letra = metadata.get('letra') or None

    if not titulo:
        print("⚠️ db_adapter.upsert_cancion: título vacío, se omite el guardado.")
        return None

    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()

            # Buscar si ya existe (titulo + artista)
            cur.execute(
                "SELECT id_cancion FROM canciones WHERE titulo = ? AND artista = ? LIMIT 1",
                (titulo, artista)
            )
            row = cur.fetchone()

            if row:
                id_cancion = row['id_cancion']
                # Actualizar ruta_local y caratula_url si tenemos nuevos valores
                cur.execute(
                    """UPDATE canciones
                       SET ruta_local    = COALESCE(?, ruta_local),
                           caratula_url  = COALESCE(?, caratula_url)
                       WHERE id_cancion  = ?""",
                    (ruta_local, caratula_url, id_cancion)
                )
                conn.commit()
                print(f"🔄 BD actualizada — canción existente: {titulo} - {artista} (id={id_cancion})")
                return id_cancion

            # Insertar nueva canción
            cur.execute(
                """INSERT INTO canciones
                   (titulo, artista, album, duracion_seg, genero,
                    plataforma_origen, url_origen, ruta_local, caratula_url, letra)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (titulo, artista, album, duracion_seg, genero,
                 plataforma_origen, url_origen, ruta_local, caratula_url, letra)
            )
            conn.commit()
            id_cancion = cur.lastrowid
            print(f"💾 BD — nueva canción guardada: {titulo} - {artista} (id={id_cancion})")
            return id_cancion

        finally:
            conn.close()

    except Exception as e:
        print(f"⚠️ db_adapter.upsert_cancion error: {e}")
        return None


def registrar_descarga(id_cancion: int, id_usuario: int = 1,
                        formato: str = 'mp3', db_path=None) -> int | None:
    """
    Registra una fila en la tabla 'descargas'.
    Usa id_usuario=1 por defecto (usuario del sistema / primer usuario semilla)
    hasta que la app tenga autenticación.

    Devuelve id_descarga o None si falla.
    """
    if not _DB_AVAILABLE:
        return None
    if not id_cancion:
        return None

    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO descargas (id_usuario, id_cancion, formato) VALUES (?, ?, ?)",
                (id_usuario, id_cancion, formato)
            )
            conn.commit()
            id_descarga = cur.lastrowid
            print(f"💾 BD — descarga registrada: id_cancion={id_cancion}, formato={formato} (id_descarga={id_descarga})")
            return id_descarga
        finally:
            conn.close()

    except Exception as e:
        print(f"⚠️ db_adapter.registrar_descarga error: {e}")
        return None
