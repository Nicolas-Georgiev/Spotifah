# db_adapter.py
"""
Capa de acceso a la BD SQLite (ekho.db) para los conversores.
Expone upsert_cancion() y registrar_descarga() que se llaman
automáticamente al terminar cada conversión a MP3.
Todas las operaciones retornan y aceptan JSON para comunicación con la BD.
"""

import os
import sys
import json

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


def _cancion_row_to_json(row) -> dict:
    """
    Convierte una fila de la tabla 'canciones' (sqlite3.Row) a un diccionario JSON.
    """
    if not row:
        return None
    
    return {
        'id_cancion': row['id_cancion'],
        'titulo': row['titulo'],
        'artista': row['artista'],
        'album': row['album'],
        'duracion_seg': row['duracion_seg'],
        'genero': row['genero'],
        'plataforma_origen': row['plataforma_origen'],
        'url_origen': row['url_origen'],
        'ruta_local': row['ruta_local'],
        'caratula_url': row['caratula_url'],
        'letra': row['letra'],
        'fecha_importacion': row['fecha_importacion']
    }


def get_cancion_json(id_cancion: int = None, titulo: str = None, 
                     artista: str = None, db_path=None) -> dict | None:
    """
    Obtiene una canción de la BD y la devuelve en formato JSON.
    
    Puede buscar por:
    - id_cancion: ID de la canción
    - titulo + artista: Búsqueda por título y artista
    
    Returns:
        dict: JSON con los datos de la canción, o None si no se encuentra
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return None
    
    if not id_cancion and not (titulo and artista):
        print("⚠️ get_cancion_json: se requiere id_cancion o (titulo + artista)")
        return None
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            
            if id_cancion:
                cur.execute(
                    "SELECT * FROM canciones WHERE id_cancion = ? LIMIT 1",
                    (id_cancion,)
                )
            else:
                cur.execute(
                    "SELECT * FROM canciones WHERE titulo = ? AND artista = ? LIMIT 1",
                    (titulo, artista)
                )
            
            row = cur.fetchone()
            if row:
                cancion_json = _cancion_row_to_json(row)
                print(f"📖 BD — canción encontrada: {cancion_json['titulo']} - {cancion_json['artista']}")
                return cancion_json
            else:
                print(f"⚠️ BD — canción no encontrada")
                return None
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ db_adapter.get_cancion_json error: {e}")
        return None


def get_todas_canciones_json(db_path=None) -> list[dict]:
    """
    Obtiene todas las canciones de la BD y las devuelve en formato JSON.
    
    Returns:
        list[dict]: Lista de JSONs con los datos de todas las canciones
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return []
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM canciones ORDER BY id_cancion")
            rows = cur.fetchall()
            
            canciones = [_cancion_row_to_json(row) for row in rows]
            print(f"📖 BD — {len(canciones)} canciones encontradas")
            return canciones
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ db_adapter.get_todas_canciones_json error: {e}")
        return []


def guardar_cancion_desde_json(cancion_json: dict | str, db_path=None) -> dict | None:
    """
    Guarda una canción en la BD desde un JSON y devuelve el JSON completo 
    con el id_cancion asignado.
    
    Args:
        cancion_json: Diccionario o string JSON con los datos de la canción
        db_path: Ruta opcional a la base de datos
    
    Returns:
        dict: JSON completo de la canción guardada (incluyendo id_cancion),
              o None si falla
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return None
    
    # Si recibimos un string JSON, convertirlo a dict
    if isinstance(cancion_json, str):
        try:
            cancion_json = json.loads(cancion_json)
        except json.JSONDecodeError as e:
            print(f"⚠️ guardar_cancion_desde_json: JSON inválido ({e})")
            return None
    
    # Usar upsert_cancion que ya maneja la lógica de inserción/actualización
    id_cancion = upsert_cancion(cancion_json, db_path)
    
    if id_cancion:
        # Obtener el JSON completo de la canción guardada
        return get_cancion_json(id_cancion=id_cancion, db_path=db_path)
    
    return None


def upsert_cancion(metadata: dict, db_path=None) -> int | None:
    """
    Inserta una canción en la tabla 'canciones' o actualiza ruta_local/caratula_url
    si ya existe (match por titulo + artista).

    Acepta tanto el formato de SpotifyInfoExtractor (claves en español)
    como el formato de YouTube2MP3Converter (claves en inglés).

    Devuelve id_cancion o None si falla.
    
    NOTA: Para obtener el JSON completo de la canción guardada, 
    usar get_cancion_json() o guardar_cancion_desde_json()
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


def upsert_cancion_json(metadata: dict, db_path=None) -> dict | None:
    """
    Inserta o actualiza una canción en la BD y devuelve el JSON completo 
    de la canción guardada.
    
    Esta es la versión mejorada de upsert_cancion que devuelve el JSON
    completo en lugar de solo el ID.

    Args:
        metadata: Diccionario con los metadatos de la canción
        db_path: Ruta opcional a la base de datos

    Returns:
        dict: JSON completo de la canción guardada, o None si falla
        
    Ejemplo de JSON retornado:
        {
            'id_cancion': 1,
            'titulo': 'Nombre de la canción',
            'artista': 'Nombre del artista',
            'album': 'Nombre del álbum',
            'duracion_seg': 240,
            'genero': 'Rock',
            'plataforma_origen': 'Spotify',
            'url_origen': 'https://...',
            'ruta_local': '/path/to/song.mp3',
            'caratula_url': 'https://...',
            'letra': 'Letra de la canción...',
            'fecha_importacion': '2026-05-20 10:30:00'
        }
    """
    # Guardar la canción usando upsert_cancion
    id_cancion = upsert_cancion(metadata, db_path)
    
    if id_cancion:
        # Obtener el JSON completo de la canción guardada
        cancion_json = get_cancion_json(id_cancion=id_cancion, db_path=db_path)
        if cancion_json:
            print(f"✅ Canción guardada y JSON generado: {cancion_json['titulo']} - {cancion_json['artista']}")
        return cancion_json
    
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


def get_playlist_json(id_playlist: int, db_path=None) -> dict | None:
    """
    Obtiene una playlist de la BD con todas sus canciones en formato JSON.
    
    Args:
        id_playlist: ID de la playlist
        db_path: Ruta opcional a la base de datos
    
    Returns:
        dict: JSON con los datos de la playlist y sus canciones, o None si no se encuentra
        
    Ejemplo de JSON retornado:
        {
            'id_playlist': 1,
            'id_usuario': 1,
            'nombre': 'Mis Favoritas',
            'descripcion': 'Canciones que me gustan',
            'fecha_creacion': '2026-05-20 10:00:00',
            'publica': 1,
            'nombre_usuario': 'Juan',
            'canciones': [
                {
                    'id_cancion': 1,
                    'titulo': 'Canción 1',
                    'artista': 'Artista A',
                    ...
                },
                ...
            ]
        }
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return None
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            
            # Obtener información de la playlist
            cur.execute("""
                SELECT p.*, u.nombre_usuario
                FROM playlists p
                LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                WHERE p.id_playlist = ?
            """, (id_playlist,))
            
            playlist_row = cur.fetchone()
            if not playlist_row:
                print(f"⚠️ BD — playlist no encontrada (id={id_playlist})")
                return None
            
            # Construir el JSON de la playlist
            playlist_json = {
                'id_playlist': playlist_row['id_playlist'],
                'id_usuario': playlist_row['id_usuario'],
                'nombre': playlist_row['nombre'],
                'descripcion': playlist_row['descripcion'],
                'fecha_creacion': playlist_row['fecha_creacion'],
                'publica': playlist_row['publica'],
                'nombre_usuario': playlist_row['nombre_usuario'],
                'canciones': []
            }
            
            # Obtener las canciones de la playlist
            cur.execute("""
                SELECT c.*, pc.orden
                FROM playlist_canciones pc
                JOIN canciones c ON pc.id_cancion = c.id_cancion
                WHERE pc.id_playlist = ?
                ORDER BY pc.orden
            """, (id_playlist,))
            
            canciones_rows = cur.fetchall()
            for cancion_row in canciones_rows:
                cancion_json = _cancion_row_to_json(cancion_row)
                cancion_json['orden'] = cancion_row['orden']
                playlist_json['canciones'].append(cancion_json)
            
            print(f"📖 BD — playlist encontrada: {playlist_json['nombre']} con {len(playlist_json['canciones'])} canciones")
            return playlist_json
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ db_adapter.get_playlist_json error: {e}")
        return None


def get_todas_playlists_json(id_usuario: int = None, db_path=None) -> list[dict]:
    """
    Obtiene todas las playlists de la BD en formato JSON.
    Opcionalmente filtra por usuario.
    
    Args:
        id_usuario: ID del usuario (opcional). Si se proporciona, solo devuelve sus playlists
        db_path: Ruta opcional a la base de datos
    
    Returns:
        list[dict]: Lista de JSONs con los datos de las playlists (sin canciones detalladas)
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return []
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            
            if id_usuario:
                cur.execute("""
                    SELECT p.*, u.nombre_usuario,
                           (SELECT COUNT(*) FROM playlist_canciones pc 
                            WHERE pc.id_playlist = p.id_playlist) as num_canciones
                    FROM playlists p
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE p.id_usuario = ?
                    ORDER BY p.id_playlist
                """, (id_usuario,))
            else:
                cur.execute("""
                    SELECT p.*, u.nombre_usuario,
                           (SELECT COUNT(*) FROM playlist_canciones pc 
                            WHERE pc.id_playlist = p.id_playlist) as num_canciones
                    FROM playlists p
                    LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                    ORDER BY p.id_playlist
                """)
            
            rows = cur.fetchall()
            playlists = []
            
            for row in rows:
                playlist_json = {
                    'id_playlist': row['id_playlist'],
                    'id_usuario': row['id_usuario'],
                    'nombre': row['nombre'],
                    'descripcion': row['descripcion'],
                    'fecha_creacion': row['fecha_creacion'],
                    'publica': row['publica'],
                    'nombre_usuario': row['nombre_usuario'],
                    'num_canciones': row['num_canciones']
                }
                playlists.append(playlist_json)
            
            print(f"📖 BD — {len(playlists)} playlists encontradas")
            return playlists
                
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ db_adapter.get_todas_playlists_json error: {e}")
        return []
