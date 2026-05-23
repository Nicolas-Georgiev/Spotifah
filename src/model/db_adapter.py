# db_adapter.py
"""
Capa de acceso a la BD SQLite (ekho.db) para los conversores.
Expone upsert_cancion() y registrar_descarga() que se llaman
automáticamente al terminar cada conversión a MP3.
Todas las operaciones retornan y aceptan JSON para comunicación con la BD.
Las imágenes se almacenan como BLOB y se codifican/decodifican en base64.
"""

import os
import sys
import json
import base64
import requests
from io import BytesIO
from pathlib import Path

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


# ==================== FUNCIONES PARA MANEJO DE IMÁGENES COMO BLOB ====================

def imagen_url_a_blob(url: str) -> bytes | None:
    """
    Descarga una imagen desde una URL y la convierte a BLOB (bytes).
    
    Args:
        url: URL de la imagen
        
    Returns:
        bytes: Imagen como BLOB, o None si falla
    """
    if not url:
        return None
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"⚠️ Error al descargar imagen desde {url}: {e}")
        return None


def imagen_archivo_a_blob(ruta: str) -> bytes | None:
    """
    Lee una imagen desde un archivo local y la convierte a BLOB (bytes).
    
    Args:
        ruta: Ruta al archivo de imagen
        
    Returns:
        bytes: Imagen como BLOB, o None si falla
    """
    if not ruta or not os.path.exists(ruta):
        return None
    
    try:
        with open(ruta, 'rb') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Error al leer imagen desde {ruta}: {e}")
        return None


def blob_a_base64(blob: bytes) -> str | None:
    """
    Convierte un BLOB a una cadena base64 para visualización.
    
    Args:
        blob: Imagen como bytes
        
    Returns:
        str: Cadena base64, o None si falla
    """
    if not blob:
        return None
    
    try:
        return base64.b64encode(blob).decode('utf-8')
    except Exception as e:
        print(f"⚠️ Error al convertir BLOB a base64: {e}")
        return None


def base64_a_blob(base64_str: str) -> bytes | None:
    """
    Convierte una cadena base64 a BLOB (bytes).
    
    Args:
        base64_str: Cadena en formato base64
        
    Returns:
        bytes: Imagen como BLOB, o None si falla
    """
    if not base64_str:
        return None
    
    try:
        return base64.b64decode(base64_str)
    except Exception as e:
        print(f"⚠️ Error al convertir base64 a BLOB: {e}")
        return None


def blob_a_data_uri(blob: bytes, mime_type: str = 'image/jpeg') -> str | None:
    """
    Convierte un BLOB a un Data URI para usar directamente en HTML/CSS.
    
    Args:
        blob: Imagen como bytes
        mime_type: Tipo MIME de la imagen (default: image/jpeg)
        
    Returns:
        str: Data URI (data:image/jpeg;base64,...), o None si falla
    """
    if not blob:
        return None
    
    try:
        base64_str = base64.b64encode(blob).decode('utf-8')
        return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        print(f"⚠️ Error al crear Data URI: {e}")
        return None


def _cancion_row_to_json(row) -> dict:
    """
    Convierte una fila de la tabla 'canciones' (sqlite3.Row) a un diccionario JSON.
    Las imágenes BLOB se convierten a base64 para visualización.
    """
    if not row:
        return None
    
    # Convertir BLOB a base64 si existe
    caratula_base64 = None
    if row['caratula_blob']:
        caratula_base64 = blob_a_base64(row['caratula_blob'])
    
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
        'caratula_base64': caratula_base64,  # Imagen decodificada en base64
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
    
    # Manejar imagen como BLOB
    caratula_blob = None
    if metadata.get('caratula_base64'):
        # Si viene en base64, convertir a BLOB
        caratula_blob = base64_a_blob(metadata['caratula_base64'])
    elif caratula_url:
        # Si tenemos URL, descargar y convertir a BLOB
        caratula_blob = imagen_url_a_blob(caratula_url)
    elif metadata.get('caratula_path'):
        # Si tenemos ruta local, leer y convertir a BLOB
        caratula_blob = imagen_archivo_a_blob(metadata['caratula_path'])

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
                # Actualizar ruta_local, caratula_url y caratula_blob si tenemos nuevos valores
                cur.execute(
                    """UPDATE canciones
                       SET ruta_local    = COALESCE(?, ruta_local),
                           caratula_url  = COALESCE(?, caratula_url),
                           caratula_blob = COALESCE(?, caratula_blob)
                       WHERE id_cancion  = ?""",
                    (ruta_local, caratula_url, caratula_blob, id_cancion)
                )
                conn.commit()
                print(f"🔄 BD actualizada — canción existente: {titulo} - {artista} (id={id_cancion})")
                return id_cancion

            # Insertar nueva canción
            cur.execute(
                """INSERT INTO canciones
                   (titulo, artista, album, duracion_seg, genero,
                    plataforma_origen, url_origen, ruta_local, caratula_url, caratula_blob, letra)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (titulo, artista, album, duracion_seg, genero,
                 plataforma_origen, url_origen, ruta_local, caratula_url, caratula_blob, letra)
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


# ==================== FUNCIONES PARA PLAYLISTS COMPLETAS COMO JSON ====================

def guardar_playlist_json_completa(id_usuario: int, nombre: str, descripcion: str = "", 
                                   canciones: list = None, publica: bool = False,
                                   caratula_url: str = None, caratula_base64: str = None,
                                   db_path=None) -> dict | None:
    """
    Guarda una playlist COMPLETA en la BD como un JSON único.
    La playlist se guarda en el campo playlist_json con todas sus canciones.
    
    Args:
        id_usuario: ID del usuario propietario
        nombre: Nombre de la playlist
        descripcion: Descripción de la playlist
        canciones: Lista de IDs de canciones o lista de dicts con info de canciones
        publica: Si la playlist es pública
        caratula_url: URL de la carátula de la playlist
        caratula_base64: Carátula en formato base64
        db_path: Ruta opcional a la BD
        
    Returns:
        dict: JSON completo de la playlist guardada, o None si falla
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return None
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            # Preparar lista de canciones con información completa
            canciones_completas = []
            if canciones:
                cur = conn.cursor()
                for idx, cancion in enumerate(canciones, 1):
                    if isinstance(cancion, int):
                        # Si es un ID, obtener la canción completa
                        cur.execute("SELECT * FROM canciones WHERE id_cancion = ?", (cancion,))
                        row = cur.fetchone()
                        if row:
                            cancion_data = _cancion_row_to_json(row)
                            cancion_data['orden'] = idx
                            canciones_completas.append(cancion_data)
                    elif isinstance(cancion, dict):
                        # Si ya es un dict, usarlo directamente
                        cancion['orden'] = idx
                        canciones_completas.append(cancion)
            
            # Manejar imagen de la playlist como BLOB
            caratula_blob = None
            if caratula_base64:
                caratula_blob = base64_a_blob(caratula_base64)
            elif caratula_url:
                caratula_blob = imagen_url_a_blob(caratula_url)
            
            # Construir el JSON completo de la playlist
            playlist_json = {
                'nombre': nombre,
                'descripcion': descripcion,
                'id_usuario': id_usuario,
                'publica': publica,
                'canciones': canciones_completas,
                'total_canciones': len(canciones_completas),
                'duracion_total': sum(c.get('duracion_seg', 0) or 0 for c in canciones_completas)
            }
            
            # Convertir a string JSON para guardar en BD
            playlist_json_str = json.dumps(playlist_json, ensure_ascii=False)
            
            # Insertar en la BD
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO playlists 
                (id_usuario, nombre, descripcion, publica, playlist_json, caratula_blob)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_usuario, nombre, descripcion, 1 if publica else 0, playlist_json_str, caratula_blob))
            
            id_playlist = cur.lastrowid
            
            # También guardar en playlist_canciones para compatibilidad (opcional)
            if canciones_completas:
                for cancion in canciones_completas:
                    id_cancion = cancion.get('id_cancion')
                    orden = cancion.get('orden', 1)
                    if id_cancion:
                        try:
                            cur.execute("""
                                INSERT INTO playlist_canciones (id_playlist, id_cancion, orden)
                                VALUES (?, ?, ?)
                            """, (id_playlist, id_cancion, orden))
                        except:
                            pass  # Ignorar errores si la canción no existe o duplicado
            
            conn.commit()
            
            # Retornar el JSON completo con el ID asignado
            playlist_json['id_playlist'] = id_playlist
            playlist_json['fecha_creacion'] = None  # Se puede obtener de la BD si se necesita
            
            # Agregar carátula en base64 si existe
            if caratula_blob:
                playlist_json['caratula_base64'] = blob_a_base64(caratula_blob)
            
            print(f"💾 Playlist guardada completa: {nombre} (ID: {id_playlist}, {len(canciones_completas)} canciones)")
            return playlist_json
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ Error al guardar playlist completa: {e}")
        import traceback
        traceback.print_exc()
        return None


def obtener_playlist_json_completa(id_playlist: int, db_path=None) -> dict | None:
    """
    Obtiene una playlist COMPLETA desde el campo playlist_json.
    Si el campo está vacío, construye el JSON desde las tablas relacionales.
    
    Args:
        id_playlist: ID de la playlist
        db_path: Ruta opcional a la BD
        
    Returns:
        dict: JSON completo de la playlist con todas sus canciones, o None si falla
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return None
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            
            # Obtener la playlist
            cur.execute("""
                SELECT p.*, u.nombre_usuario
                FROM playlists p
                LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
                WHERE p.id_playlist = ?
            """, (id_playlist,))
            
            row = cur.fetchone()
            if not row:
                print(f"⚠️ Playlist no encontrada (ID: {id_playlist})")
                return None
            
            # Si existe playlist_json, usarlo
            if row['playlist_json']:
                try:
                    playlist_data = json.loads(row['playlist_json'])
                    playlist_data['id_playlist'] = row['id_playlist']
                    playlist_data['fecha_creacion'] = row['fecha_creacion']
                    playlist_data['nombre_usuario'] = row['nombre_usuario']
                    
                    # Agregar carátula en base64 si existe
                    if row['caratula_blob']:
                        playlist_data['caratula_base64'] = blob_a_base64(row['caratula_blob'])
                    
                    print(f"📖 Playlist obtenida desde JSON: {playlist_data['nombre']} ({len(playlist_data.get('canciones', []))} canciones)")
                    return playlist_data
                except json.JSONDecodeError:
                    print("⚠️ JSON de playlist corrupto, reconstruyendo desde tablas relacionales...")
            
            # Si no hay playlist_json o está corrupto, construir desde tablas relacionales
            playlist_json = {
                'id_playlist': row['id_playlist'],
                'id_usuario': row['id_usuario'],
                'nombre': row['nombre'],
                'descripcion': row['descripcion'],
                'fecha_creacion': row['fecha_creacion'],
                'publica': row['publica'],
                'nombre_usuario': row['nombre_usuario'],
                'canciones': []
            }
            
            # Obtener canciones de playlist_canciones
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
            
            playlist_json['total_canciones'] = len(playlist_json['canciones'])
            playlist_json['duracion_total'] = sum(c.get('duracion_seg', 0) or 0 for c in playlist_json['canciones'])
            
            # Agregar carátula en base64 si existe
            if row['caratula_blob']:
                playlist_json['caratula_base64'] = blob_a_base64(row['caratula_blob'])
            
            print(f"📖 Playlist obtenida desde tablas: {playlist_json['nombre']} ({len(playlist_json['canciones'])} canciones)")
            return playlist_json
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ Error al obtener playlist completa: {e}")
        import traceback
        traceback.print_exc()
        return None


def actualizar_playlist_json_completa(id_playlist: int, nombre: str = None, 
                                     descripcion: str = None, canciones: list = None,
                                     publica: bool = None, caratula_url: str = None,
                                     caratula_base64: str = None, db_path=None) -> dict | None:
    """
    Actualiza una playlist completa guardando todo en playlist_json.
    
    Args:
        id_playlist: ID de la playlist a actualizar
        nombre: Nuevo nombre (opcional)
        descripcion: Nueva descripción (opcional)
        canciones: Nueva lista de canciones (opcional)
        publica: Nueva visibilidad (opcional)
        caratula_url: Nueva URL de carátula (opcional)
        caratula_base64: Nueva carátula en base64 (opcional)
        db_path: Ruta opcional a la BD
        
    Returns:
        dict: JSON completo actualizado, o None si falla
    """
    if not _DB_AVAILABLE:
        print("⚠️ BD no disponible")
        return None
    
    # Primero obtener la playlist actual
    playlist_actual = obtener_playlist_json_completa(id_playlist, db_path)
    if not playlist_actual:
        print(f"⚠️ No se puede actualizar playlist {id_playlist}: no existe")
        return None
    
    try:
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            
            # Actualizar los campos que se especifiquen
            if nombre is not None:
                playlist_actual['nombre'] = nombre
            if descripcion is not None:
                playlist_actual['descripcion'] = descripcion
            if publica is not None:
                playlist_actual['publica'] = publica
            
            # Actualizar canciones si se especifican
            if canciones is not None:
                canciones_completas = []
                for idx, cancion in enumerate(canciones, 1):
                    if isinstance(cancion, int):
                        # Si es un ID, obtener la canción completa
                        cur.execute("SELECT * FROM canciones WHERE id_cancion = ?", (cancion,))
                        row = cur.fetchone()
                        if row:
                            cancion_data = _cancion_row_to_json(row)
                            cancion_data['orden'] = idx
                            canciones_completas.append(cancion_data)
                    elif isinstance(cancion, dict):
                        cancion['orden'] = idx
                        canciones_completas.append(cancion)
                
                playlist_actual['canciones'] = canciones_completas
                playlist_actual['total_canciones'] = len(canciones_completas)
                playlist_actual['duracion_total'] = sum(c.get('duracion_seg', 0) or 0 for c in canciones_completas)
            
            # Manejar nueva carátula
            caratula_blob = None
            if caratula_base64:
                caratula_blob = base64_a_blob(caratula_base64)
            elif caratula_url:
                caratula_blob = imagen_url_a_blob(caratula_url)
            
            # Convertir a JSON string
            playlist_json_str = json.dumps(playlist_actual, ensure_ascii=False)
            
            # Actualizar en BD
            updates = []
            params = []
            
            if nombre is not None:
                updates.append("nombre = ?")
                params.append(nombre)
            if descripcion is not None:
                updates.append("descripcion = ?")
                params.append(descripcion)
            if publica is not None:
                updates.append("publica = ?")
                params.append(1 if publica else 0)
            
            updates.append("playlist_json = ?")
            params.append(playlist_json_str)
            
            if caratula_blob is not None:
                updates.append("caratula_blob = ?")
                params.append(caratula_blob)
            
            params.append(id_playlist)
            
            query = f"UPDATE playlists SET {', '.join(updates)} WHERE id_playlist = ?"
            cur.execute(query, params)
            
            # Actualizar playlist_canciones si se cambiaron las canciones
            if canciones is not None:
                # Eliminar canciones actuales
                cur.execute("DELETE FROM playlist_canciones WHERE id_playlist = ?", (id_playlist,))
                
                # Insertar nuevas
                for cancion in playlist_actual['canciones']:
                    id_cancion = cancion.get('id_cancion')
                    orden = cancion.get('orden', 1)
                    if id_cancion:
                        try:
                            cur.execute("""
                                INSERT INTO playlist_canciones (id_playlist, id_cancion, orden)
                                VALUES (?, ?, ?)
                            """, (id_playlist, id_cancion, orden))
                        except:
                            pass
            
            conn.commit()
            
            # Agregar carátula actualizada en base64
            if caratula_blob:
                playlist_actual['caratula_base64'] = blob_a_base64(caratula_blob)
            
            print(f"🔄 Playlist actualizada: {playlist_actual['nombre']} (ID: {id_playlist})")
            return playlist_actual
            
        finally:
            conn.close()
            
    except Exception as e:
        print(f"⚠️ Error al actualizar playlist completa: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_id_cancion_por_ruta(ruta_local: str, db_path=None) -> int | None:
    """Devuelve el id_cancion de la canción cuya ruta_local coincide."""
    if not _DB_AVAILABLE or not ruta_local:
        return None
    try:
        ruta_norm = os.path.normpath(os.path.abspath(ruta_local))
        db = _get_db(db_path)
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id_cancion FROM canciones WHERE ruta_local = ? OR ruta_local = ?",
                (ruta_norm, ruta_local),
            )
            row = cur.fetchone()
            return row['id_cancion'] if row else None
        finally:
            conn.close()
    except Exception as e:
        print(f"⚠️ db_adapter.get_id_cancion_por_ruta error: {e}")
        return None
