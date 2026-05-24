import os
import sqlite3
import sys
from pathlib import Path

if __package__ is None:
    src_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(src_dir))

try:
    from .db import Database
except Exception:
    from databaseManager.db import Database

def create_song(conn: sqlite3.Connection):
    print("\nCrear nueva canción")
    title = input("Título: ").strip()
    if not title:
        print("Título obligatorio.")
        return
    artist = input("Artista (opcional): ").strip() or None
    album = input("Álbum (opcional): ").strip() or None
    try:
        dur = input("Duración en segundos (opcional): ").strip()
        duration_sec = int(dur) if dur else None
    except ValueError:
        print("Duración inválida.")
        return
    genre = input("Género (opcional): ").strip() or None
    platform = input("Plataforma origen (por defecto 'local'): ").strip() or "local"
    source_url = input("URL origen (opcional): ").strip() or None
    local_path = input("Ruta local (opcional): ").strip() or None
    cover = input("URL carátula (opcional): ").strip() or None
    lyrics = input("Letra (opcional): ").strip() or None

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO canciones
        (titulo, artista, album, duracion_seg, genero, plataforma_origen, url_origen, ruta_local, caratula_url, letra)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (title, artist, album, duration_sec, genre, platform, source_url, local_path, cover, lyrics))
    conn.commit()
    print(f"Canción creada con id {cur.lastrowid}.")

def list_songs(conn: sqlite3.Connection):
    cur = conn.execute("SELECT id_cancion, titulo, artista, genero, duracion_seg FROM canciones ORDER BY id_cancion")
    rows = cur.fetchall()
    if not rows:
        print("\nNo hay canciones.")
        return
    print("\nCanciones:")
    for r in rows:
        print(f"  {r['id_cancion']}: {r['titulo']} - {r['artista'] or '-'} ({r['genero'] or '-'}, {r['duracion_seg'] or '-'}s)")

def list_users(conn: sqlite3.Connection):
    cur = conn.execute("SELECT id_usuario, nombre_usuario, correo FROM usuarios ORDER BY id_usuario")
    rows = cur.fetchall()
    if not rows:
        print("\nNo hay usuarios.")
        return []
    print("\nUsuarios:")
    for r in rows:
        print(f"  {r['id_usuario']}: {r['nombre_usuario']} <{r['correo']}>")
    return rows

def create_user(conn: sqlite3.Connection):
    print("\nCrear nuevo usuario")
    username = input("Nombre de usuario: ").strip()
    if not username:
        print("Nombre de usuario obligatorio.")
        return
    email = input("Correo: ").strip()
    if not email:
        print("Correo obligatorio.")
        return
    password = input("Contraseña (hash): ").strip()
    if not password:
        print("Contraseña obligatoria.")
        return
    country = input("País (opcional): ").strip() or None
    genre_preferences = input("Géneros preferidos JSON (opcional, ej: [\"Pop\",\"Rock\"]): ").strip() or None
    artist_preferences = input("Artistas preferidos JSON (opcional, ej: [\"Artista A\"]): ").strip() or None

    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre_usuario, correo, contraseña_hash, pais, preferencias_generos, preferencias_artistas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, password, country, genre_preferences, artist_preferences))
        conn.commit()
        print(f"Usuario creado con id {cur.lastrowid}.")
    except sqlite3.IntegrityError:
        print("Error: El correo ya existe.")

def create_playlist(conn: sqlite3.Connection):
    print("\nCrear nueva playlist")
    users = list_users(conn)
    if not users:
        print("No hay usuarios para asignar la playlist.")
        return
    try:
        user_id = int(input("ID de usuario propietario (elige de la lista): ").strip())
    except ValueError:
        print("ID inválido.")
        return
    name = input("Nombre playlist: ").strip()
    if not name:
        print("Nombre obligatorio.")
        return
    description = input("Descripción (opcional): ").strip() or None
    is_public_input = input("¿Pública? (s/N): ").strip().lower()
    is_public = 1 if is_public_input == 's' else 0

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO playlists (id_usuario, nombre, descripcion, publica)
        VALUES (?, ?, ?, ?)
    """, (user_id, name, description, is_public))
    conn.commit()
    print(f"Playlist creada con id {cur.lastrowid}.")

def list_playlists(conn: sqlite3.Connection):
    cur = conn.execute("""
        SELECT p.id_playlist, p.nombre, p.descripcion, p.publica, u.nombre_usuario
        FROM playlists p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        ORDER BY p.id_playlist
    """)
    rows = cur.fetchall()
    if not rows:
        print("\nNo hay playlists.")
        return
    print("\nPlaylists:")
    for r in rows:
        pub = "Pública" if r["publica"] else "Privada"
        print(f"  {r['id_playlist']}: {r['nombre']} ({pub}) - creador: {r['nombre_usuario'] or '-'}")

def view_playlist_songs(conn: sqlite3.Connection):
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
        playlist_id = int(input("\nIngresa el ID de la playlist que deseas ver: ").strip())
    except ValueError:
        print("ID inválido.")
        return

    cur = conn.execute("""
        SELECT p.id_playlist, p.nombre, p.descripcion, p.publica, u.nombre_usuario
        FROM playlists p
        LEFT JOIN usuarios u ON p.id_usuario = u.id_usuario
        WHERE p.id_playlist = ?
    """, (playlist_id,))
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
    """, (playlist_id,))
    songs = cur.fetchall()

    if not songs:
        print("\nEsta playlist no tiene canciones.")
    else:
        print(f"\nCanciones ({len(songs)}):")
        for idx, c in enumerate(songs, 1):
            print(f"  {idx}. {c['titulo']} - {c['artista'] or '-'} ({c['genero'] or '-'}, {c['duracion_seg'] or '-'}s)")

def add_song_to_playlist(conn: sqlite3.Connection):
    print("\nAñadir canción a playlist")
    list_playlists(conn)
    try:
        playlist_id = int(input("ID playlist: ").strip())
    except ValueError:
        print("ID inválido.")
        return
    list_songs(conn)
    try:
        song_id = int(input("ID canción: ").strip())
    except ValueError:
        print("ID canción inválido.")
        return
    order_input = input("Orden en la playlist (opcional, por defecto 1): ").strip()
    try:
        order = int(order_input) if order_input else 1
    except ValueError:
        print("Orden inválido.")
        return
    try:
        conn.execute("""
            INSERT INTO playlist_canciones (id_playlist, id_cancion, orden)
            VALUES (?, ?, ?)
        """, (playlist_id, song_id, order))
        conn.commit()
        print("Canción añadida a la playlist.")
    except sqlite3.IntegrityError as e:
        print(f"Error al añadir: {e}")

def run_menu(conn: sqlite3.Connection):
    actions = {
        "1": ("Listar canciones", lambda: list_songs(conn)),
        "2": ("Crear canción", lambda: create_song(conn)),
        "3": ("Listar usuarios", lambda: list_users(conn)),
        "4": ("Crear usuario", lambda: create_user(conn)),
        "5": ("Listar playlists", lambda: list_playlists(conn)),
        "6": ("Ver playlist con canciones", lambda: view_playlist_songs(conn)),
        "7": ("Crear playlist", lambda: create_playlist(conn)),
        "8": ("Añadir canción a playlist", lambda: add_song_to_playlist(conn)),
        "0": ("Salir", None)
    }

    while True:
        print("\n=== Menú Spotifah (CLI) ===")
        for k, v in actions.items():
            print(f"  {k}. {v[0]}")
        choice = input("Elige una opción: ").strip()
        if choice == "0":
            print("Saliendo...")
            break
        action = actions.get(choice)
        if action and action[1]:
            action[1]()
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
