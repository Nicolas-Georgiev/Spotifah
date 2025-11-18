import os
import sqlite3
import sys
from pathlib import Path

# Permitir ejecutar este archivo directamente (fallback) y mantener la import relativa cuando se ejecuta como paquete.
if __package__ is None:
    # añade 'src' al sys.path para que 'databaseManager' sea importable cuando ejecutas el archivo directamente
    src_dir = Path(__file__).resolve().parents[1]  # ../.. -> .../src
    sys.path.insert(0, str(src_dir))

try:
    from .db import Database
except Exception:
    # fallback para ejecución directa
    from databaseManager.db import Database

def crear_cancion(conn: sqlite3.Connection):
    print("\nCrear nueva canción")
    titulo = input("Título: ").strip()
    if not titulo:
        print("Título obligatorio.")
        return
    artista = input("Artista (opcional): ").strip() or None
    album = input("Álbum (opcional): ").strip() or None
    try:
        duracion = input("Duración en segundos (opcional): ").strip()
        duracion_seg = int(duracion) if duracion else None
    except ValueError:
        print("Duración inválida.")
        return
    genero = input("Género (opcional): ").strip() or None
    plataforma = input("Plataforma origen (por defecto 'local'): ").strip() or "local"
    url_origen = input("URL origen (opcional): ").strip() or None
    ruta_local = input("Ruta local (opcional): ").strip() or None
    caratula = input("URL carátula (opcional): ").strip() or None
    letra = input("Letra (opcional): ").strip() or None

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO canciones
        (titulo, artista, album, duracion_seg, genero, plataforma_origen, url_origen, ruta_local, caratula_url, letra)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (titulo, artista, album, duracion_seg, genero, plataforma, url_origen, ruta_local, caratula, letra))
    conn.commit()
    print(f"Canción creada con id {cur.lastrowid}.")

def listar_canciones(conn: sqlite3.Connection):
    cur = conn.execute("SELECT id_cancion, titulo, artista, genero, duracion_seg FROM canciones ORDER BY id_cancion")
    filas = cur.fetchall()
    if not filas:
        print("\nNo hay canciones.")
        return
    print("\nCanciones:")
    for r in filas:
        print(f"  {r['id_cancion']}: {r['titulo']} - {r['artista'] or '-'} ({r['genero'] or '-'}, {r['duracion_seg'] or '-'}s)")

def listar_usuarios(conn: sqlite3.Connection):
    cur = conn.execute("SELECT id_usuario, nombre_usuario, correo FROM usuarios ORDER BY id_usuario")
    filas = cur.fetchall()
    if not filas:
        print("\nNo hay usuarios.")
        return []
    print("\nUsuarios:")
    for r in filas:
        print(f"  {r['id_usuario']}: {r['nombre_usuario']} <{r['correo']}>")
    return filas

def crear_usuario(conn: sqlite3.Connection):
    print("\nCrear nuevo usuario")
    nombre_usuario = input("Nombre de usuario: ").strip()
    if not nombre_usuario:
        print("Nombre de usuario obligatorio.")
        return
    correo = input("Correo: ").strip()
    if not correo:
        print("Correo obligatorio.")
        return
    contraseña = input("Contraseña (hash): ").strip()
    if not contraseña:
        print("Contraseña obligatoria.")
        return
    pais = input("País (opcional): ").strip() or None
    preferencias_generos = input("Géneros preferidos JSON (opcional, ej: [\"Pop\",\"Rock\"]): ").strip() or None
    preferencias_artistas = input("Artistas preferidos JSON (opcional, ej: [\"Artista A\"]): ").strip() or None

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre_usuario, correo, contraseña_hash, pais, preferencias_generos, preferencias_artistas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nombre_usuario, correo, contraseña, pais, preferencias_generos, preferencias_artistas))
        conn.commit()
        print(f"Usuario creado con id {cur.lastrowid}.")
    except sqlite3.IntegrityError:
        print("Error: El correo ya existe.")

def crear_playlist(conn: sqlite3.Connection):
    print("\nCrear nueva playlist")
    usuarios = listar_usuarios(conn)
    if not usuarios:
        print("No hay usuarios para asignar la playlist.")
        return
    try:
        id_usuario = int(input("ID de usuario propietario (elige de la lista): ").strip())
    except ValueError:
        print("ID inválido.")
        return
    nombre = input("Nombre playlist: ").strip()
    if not nombre:
        print("Nombre obligatorio.")
        return
    descripcion = input("Descripción (opcional): ").strip() or None
    publica_in = input("¿Pública? (s/N): ").strip().lower()
    publica = 1 if publica_in == 's' else 0

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO playlists (id_usuario, nombre, descripcion, publica)
        VALUES (?, ?, ?, ?)
    """, (id_usuario, nombre, descripcion, publica))
    conn.commit()
    print(f"Playlist creada con id {cur.lastrowid}.")

def listar_playlists(conn: sqlite3.Connection):
    cur = conn.execute("""
        SELECT p.id_playlist, p.nombre, p.descripcion, p.publica, u.nombre_usuario
        FROM playlists p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.id_playlist
    """)
    filas = cur.fetchall()
    if not filas:
        print("\nNo hay playlists.")
        return
    print("\nPlaylists:")
    for r in filas:
        pub = "Pública" if r["publica"] else "Privada"
        print(f"  {r['id_playlist']}: {r['nombre']} ({pub}) - creador: {r['nombre_usuario'] or '-'}")

def ver_playlist_canciones(conn: sqlite3.Connection):
    print("\nVer playlist con canciones")
    
    cur = conn.execute("""
        SELECT p.id_playlist, p.nombre, p.descripcion, p.publica, u.nombre_usuario
        FROM playlists p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.id_playlist
    """)
    playlists = cur.fetchall()
    
    if not playlists:
        print("No hay playlists disponibles.")
        return
    
    print("\nPlaylists disponibles:")
    for p in playlists:
        pub = "Pública" if p["publica"] else "Privada"
        print(f"  {p['id_playlist']}: {p['nombre']} ({pub}) - creador: {p['nombre_usuario'] or '-'}")
    
    try:
        id_playlist = int(input("\nIngresa el ID de la playlist que deseas ver: ").strip())
    except ValueError:
        print("ID inválido.")
        return

    cur = conn.execute("""
        SELECT p.id_playlist, p.nombre, p.descripcion, p.publica, u.nombre_usuario
        FROM playlists p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE p.id_playlist = ?
    """, (id_playlist,))
    playlist = cur.fetchone()

    if not playlist:
        print("Playlist no encontrada.")
        return

    print(f"\n{'='*60}")
    print(f"Playlist: {playlist['nombre']}")
    print(f"Creador: {playlist['nombre_usuario'] or '-'}")
    print(f"Descripción: {playlist['descripcion'] or '-'}")
    print(f"Estado: {'Pública' if playlist['publica'] else 'Privada'}")
    print(f"{'='*60}")

    cur = conn.execute("""
        SELECT c.id_cancion, c.titulo, c.artista, c.genero, c.duracion_seg, pc.orden
        FROM playlist_canciones pc
        JOIN canciones c ON pc.id_cancion = c.id_cancion
        WHERE pc.id_playlist = ?
        ORDER BY pc.orden
    """, (id_playlist,))
    canciones = cur.fetchall()

    if not canciones:
        print("\nEsta playlist no tiene canciones.")
    else:
        print(f"\nCanciones ({len(canciones)}):")
        for idx, c in enumerate(canciones, 1):
            print(f"  {idx}. {c['titulo']} - {c['artista'] or '-'} ({c['genero'] or '-'}, {c['duracion_seg'] or '-'}s)")

def anadir_cancion_a_playlist(conn: sqlite3.Connection):
    print("\nAñadir canción a playlist")
    listar_playlists(conn)
    try:
        id_playlist = int(input("ID playlist: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    listar_canciones(conn)
    try:
        id_cancion = int(input("ID canción: ").strip())
    except ValueError:
        print("ID canción inválido.")
        return
    orden_in = input("Orden en la playlist (opcional, por defecto 1): ").strip()
    try:
        orden = int(orden_in) if orden_in else 1
    except ValueError:
        print("Orden inválido.")
        return
    try:
        conn.execute("""
            INSERT INTO playlist_canciones (id_playlist, id_cancion, orden)
            VALUES (?, ?, ?)
        """, (id_playlist, id_cancion, orden))
        conn.commit()
        print("Canción añadida a la playlist.")
    except sqlite3.IntegrityError as e:
        print(f"Error al añadir: {e}")

def run_menu(conn: sqlite3.Connection):
    acciones = {
        "1": ("Listar canciones", lambda: listar_canciones(conn)),
        "2": ("Crear canción", lambda: crear_cancion(conn)),
        "3": ("Listar usuarios", lambda: listar_usuarios(conn)),
        "4": ("Crear usuario", lambda: crear_usuario(conn)),
        "5": ("Listar playlists", lambda: listar_playlists(conn)),
        "6": ("Ver playlist con canciones", lambda: ver_playlist_canciones(conn)),
        "7": ("Crear playlist", lambda: crear_playlist(conn)),
        "8": ("Añadir canción a playlist", lambda: anadir_cancion_a_playlist(conn)),
        "0": ("Salir", None)
    }

    while True:
        print("\n=== Menú Spotifah (CLI) ===")
        for k, v in acciones.items():
            print(f"  {k}. {v[0]}")
        choice = input("Elige una opción: ").strip()
        if choice == "0":
            print("Saliendo...")
            break
        accion = acciones.get(choice)
        if accion and accion[1]:
            accion[1]()
        else:
            print("Opción no válida.")

def main():
    db_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "BDD", "ekho.db")
    db = Database(db_file)
    conn = db.get_connection()
    try:
        run_menu(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
