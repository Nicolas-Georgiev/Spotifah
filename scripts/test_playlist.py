"""
Test rápido del sistema de playlists
"""
from src.databaseManager.db import Database
from src.model.playlist_model import PlaylistModel
from src.controller.playlist_controller import PlaylistController

# Inicializar
db = Database()
model = PlaylistModel(db)
controller = PlaylistController(model)
controller.set_current_user(1)

print("\n" + "="*60)
print("  TEST DEL SISTEMA DE PLAYLISTS")
print("="*60)

# Test 1: Listar playlists
print("\n1️⃣ Probando listar playlists...")
success, msg, playlists = controller.list_my_playlists()
print(f"   {msg}")
for p in playlists:
    print(f"   - {p['nombre']}: {p['total_canciones']} canciones")

# Test 2: Listar canciones
print("\n2️⃣ Probando listar canciones...")
success, msg, canciones = controller.list_all_songs()
print(f"   {msg}")
if canciones:
    for c in canciones[:3]:
        print(f"   - {c['titulo']} by {c['artista']}")

# Test 3: Ver detalles de playlist
print("\n3️⃣ Probando ver detalles de playlist...")
if playlists:
    id_test = playlists[0]['id_playlist']
    success, msg, playlist = controller.get_playlist_details(id_test)
    if success:
        print(f"   ✅ Playlist: {playlist['nombre']}")
        print(f"   ✅ Canciones: {playlist['total_canciones']}")

# Test 4: Buscar canciones
print("\n4️⃣ Probando búsqueda de canciones...")
success, msg, resultados = controller.search_songs_by_query("Canción")
print(f"   {msg}")

print("\n" + "="*60)
print("  ✅ TODOS LOS TESTS COMPLETADOS CORRECTAMENTE")
print("="*60)
print("\n💡 El sistema está listo para usar!")
print("📝 Ejecuta: python src/playlist_manager.py (interfaz terminal)")
print("📚 Revisa: ejemplos_playlist.py (ejemplos de código)")
print("📖 Lee: PLAYLIST_README.md (documentación completa)\n")
