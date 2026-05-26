"""
EJEMPLOS DE USO DEL SISTEMA DE GESTIÓN DE PLAYLISTS
====================================================

Este archivo muestra cómo usar las funciones del sistema de playlists
de manera programática, sin la interfaz de terminal.

Ideal para cuando quieras integrar estas funciones en una interfaz gráfica (GUI).
"""

# ==================== CONFIGURACIÓN INICIAL ====================

from src.databaseManager.db import Database
from src.model.playlist_model import PlaylistModel
from src.controller.playlist_controller import PlaylistController

# Inicializar el sistema
db = Database()
model = PlaylistModel(db)
controller = PlaylistController(model)

# Establecer el usuario actual (cambiar según tu sistema de login)
controller.set_current_user(1)  # Usuario ID 1


# ==================== EJEMPLO 1: CREAR UNA PLAYLIST ====================

def ejemplo_crear_playlist():
    """Crea una nueva playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Crear una playlist")
    print("="*60)
    
    success, message, id_playlist = controller.create_new_playlist(
        nombre="Mi Playlist de Rock",
        descripcion="Las mejores canciones de rock",
        publica=True
    )
    
    print(f"[OK] {message}")
    if success:
        print(f"ID de la playlist creada: {id_playlist}")
        return id_playlist
    return None


# ==================== EJEMPLO 2: LISTAR PLAYLISTS ====================

def ejemplo_listar_playlists():
    """Lista todas las playlists del usuario"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Listar mis playlists")
    print("="*60)
    
    success, message, playlists = controller.list_my_playlists()
    
    print(f"{message}\n")
    for playlist in playlists:
        print(f"[LIST] [{playlist['id_playlist']}] {playlist['nombre']}")
        print(f"   [MUSIC] {playlist['total_canciones']} canciones")
        print(f"   {'[GLOBE] Pública' if playlist['publica'] else '[LOCK] Privada'}")


# ==================== EJEMPLO 3: VER DETALLES DE PLAYLIST ====================

def ejemplo_ver_detalles_playlist(id_playlist):
    """Obtiene información detallada de una playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Ver detalles de playlist")
    print("="*60)
    
    success, message, playlist = controller.get_playlist_details(id_playlist)
    
    if success:
        print(f"\n[LIST] {playlist['nombre']}")
        print(f"[NOTE] {playlist.get('descripcion', 'Sin descripción')}")
        print(f"[USER] Creador: {playlist['nombre_usuario']}")
        print(f"[MUSIC] Canciones: {playlist['total_canciones']}")
    else:
        print(f"[ERR] {message}")


# ==================== EJEMPLO 4: LISTAR CANCIONES ====================

def ejemplo_listar_canciones():
    """Lista todas las canciones disponibles"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Listar todas las canciones")
    print("="*60)
    
    success, message, canciones = controller.list_all_songs()
    
    print(f"{message}\n")
    for cancion in canciones[:5]:  # Mostrar solo las primeras 5
        print(f"[MUSIC] [{cancion['id_cancion']}] {cancion['titulo']}")
        print(f"   [USER] {cancion['artista']} | [DISC] {cancion.get('album', 'N/A')}")


# ==================== EJEMPLO 5: AÑADIR CANCIÓN A PLAYLIST ====================

def ejemplo_añadir_cancion(id_playlist, id_cancion):
    """Añade una canción a una playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 5: Añadir canción a playlist")
    print("="*60)
    
    success, message = controller.add_song_to_playlist_by_id(id_playlist, id_cancion)
    print(f"{message}")
    
    return success


# ==================== EJEMPLO 6: VER CANCIONES DE UNA PLAYLIST ====================

def ejemplo_ver_canciones_playlist(id_playlist):
    """Muestra las canciones de una playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 6: Ver canciones de una playlist")
    print("="*60)
    
    success, message, canciones = controller.view_playlist_songs(id_playlist)
    
    print(f"{message}\n")
    for cancion in canciones:
        orden = cancion.get('orden', 0)
        print(f"[{orden}] [MUSIC] {cancion['titulo']} - {cancion['artista']}")


# ==================== EJEMPLO 7: BUSCAR CANCIONES ====================

def ejemplo_buscar_canciones(query):
    """Busca canciones por texto"""
    print("\n" + "="*60)
    print(f"EJEMPLO 7: Buscar canciones con '{query}'")
    print("="*60)
    
    success, message, canciones = controller.search_songs_by_query(query)
    
    print(f"{message}\n")
    for cancion in canciones:
        print(f"[MUSIC] [{cancion['id_cancion']}] {cancion['titulo']} - {cancion['artista']}")


# ==================== EJEMPLO 8: ELIMINAR CANCIÓN DE PLAYLIST ====================

def ejemplo_eliminar_cancion(id_playlist, id_cancion):
    """Elimina una canción de una playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 8: Eliminar canción de playlist")
    print("="*60)
    
    success, message = controller.remove_song_from_playlist_by_id(id_playlist, id_cancion)
    print(f"{message}")


# ==================== EJEMPLO 9: EDITAR PLAYLIST ====================

def ejemplo_editar_playlist(id_playlist):
    """Modifica los datos de una playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 9: Editar playlist")
    print("="*60)
    
    success, message = controller.modify_playlist(
        id_playlist,
        nombre="Mi Playlist de Rock Actualizada",
        descripcion="La mejor colección de rock actualizada",
        publica=False  # Cambiar a privada
    )
    
    print(f"{message}")


# ==================== EJEMPLO 10: RESUMEN COMPLETO ====================

def ejemplo_resumen_playlist(id_playlist):
    """Obtiene un resumen completo de la playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 10: Resumen completo de playlist")
    print("="*60)
    
    success, message, resumen = controller.get_playlist_summary(id_playlist)
    
    if success:
        playlist = resumen['playlist']
        print(f"\n[LIST] {playlist['nombre']}")
        print(f"[CHART] Total de canciones: {resumen['total_canciones']}")
        print(f"[TIMER] Duración total: {resumen['duracion_total_min']} minutos")
        print(f"\n[MUSIC] Canciones:")
        for cancion in resumen['canciones']:
            print(f"   • {cancion['titulo']} - {cancion['artista']}")
    else:
        print(f"[ERR] {message}")


# ==================== EJEMPLO 11: ELIMINAR PLAYLIST ====================

def ejemplo_eliminar_playlist(id_playlist):
    """Elimina una playlist"""
    print("\n" + "="*60)
    print("EJEMPLO 11: Eliminar playlist")
    print("="*60)
    
    success, message = controller.remove_playlist(id_playlist)
    print(f"{message}")


# ==================== EJEMPLO DE USO DIRECTO DEL MODELO ====================

def ejemplo_uso_directo_modelo():
    """
    Ejemplo de cómo usar el modelo directamente (sin controlador)
    Útil si quieres tener control total o hacer operaciones muy específicas
    """
    print("\n" + "="*60)
    print("EJEMPLO: Uso directo del modelo")
    print("="*60)
    
    # Obtener todas las playlists directamente del modelo
    playlists = model.get_all_playlists()
    print(f"\nTotal de playlists en el sistema: {len(playlists)}")
    
    # Obtener todas las canciones
    canciones = model.get_all_songs()
    print(f"Total de canciones en el sistema: {len(canciones)}")
    
    # Crear una playlist directamente
    id_nueva = model.create_playlist(
        id_usuario=1,
        nombre="Playlist Directa",
        descripcion="Creada usando el modelo directamente"
    )
    print(f"Playlist creada con ID: {id_nueva}")


# ==================== FUNCIÓN PARA EJECUTAR TODOS LOS EJEMPLOS ====================

def ejecutar_todos_los_ejemplos():
    """Ejecuta una demostración completa del sistema"""
    print("\n")
    print("="*60)
    print("  DEMOSTRACIÓN DEL SISTEMA DE GESTIÓN DE PLAYLISTS")
    print("="*60)
    
    # Ejemplo 1: Crear playlist
    id_playlist = ejemplo_crear_playlist()
    
    if id_playlist:
        # Ejemplo 2: Listar playlists
        ejemplo_listar_playlists()
        
        # Ejemplo 3: Ver detalles
        ejemplo_ver_detalles_playlist(id_playlist)
        
        # Ejemplo 4: Listar canciones
        ejemplo_listar_canciones()
        
        # Ejemplo 5: Añadir canciones (IDs 1 y 2 de la BD de ejemplo)
        ejemplo_añadir_cancion(id_playlist, 1)
        ejemplo_añadir_cancion(id_playlist, 2)
        
        # Ejemplo 6: Ver canciones de la playlist
        ejemplo_ver_canciones_playlist(id_playlist)
        
        # Ejemplo 7: Buscar canciones
        ejemplo_buscar_canciones("Canción")
        
        # Ejemplo 9: Editar playlist
        ejemplo_editar_playlist(id_playlist)
        
        # Ejemplo 10: Resumen completo
        ejemplo_resumen_playlist(id_playlist)
        
        # Ejemplo 8: Eliminar una canción
        ejemplo_eliminar_cancion(id_playlist, 1)
        
        # Ver canciones después de eliminar
        ejemplo_ver_canciones_playlist(id_playlist)
        
        # Ejemplo 11: Eliminar playlist (comentado por defecto)
        # ejemplo_eliminar_playlist(id_playlist)
    
    # Ejemplo de uso directo del modelo
    ejemplo_uso_directo_modelo()
    
    print("\n")
    print("="*60)
    print("  FIN DE LA DEMOSTRACIÓN")
    print("="*60)
    print("\n")


# ==================== GUÍA PARA INTEGRACIÓN EN GUI ====================

"""
GUÍA PARA INTEGRAR EN INTERFAZ GRÁFICA (GUI)
=============================================

1. INICIALIZACIÓN (una vez al inicio):
   
   db = Database()
   model = PlaylistModel(db)
   controller = PlaylistController(model)
   controller.set_current_user(user_id)


2. EJEMPLOS DE INTEGRACIÓN:

   # Botón "Crear Playlist":
   def on_btn_crear_clicked():
       nombre = input_nombre.get_text()
       desc = input_desc.get_text()
       publica = checkbox_publica.is_checked()
       
       success, message, id_playlist = controller.create_new_playlist(nombre, desc, publica)
       
       if success:
           mostrar_mensaje_exito(message)
           actualizar_lista_playlists()
       else:
           mostrar_mensaje_error(message)
   
   
   # Cargar lista de playlists en un ListView/TableView:
   def cargar_playlists_en_lista():
       success, message, playlists = controller.list_my_playlists()
       
       lista_widget.clear()
       for playlist in playlists:
           item = ListItem(
               id=playlist['id_playlist'],
               titulo=playlist['nombre'],
               subtitulo=f"{playlist['total_canciones']} canciones"
           )
           lista_widget.add_item(item)
   
   
   # Añadir canción a playlist (drag & drop o botón):
   def on_song_dropped_on_playlist(id_cancion, id_playlist):
       success, message = controller.add_song_to_playlist_by_id(id_playlist, id_cancion)
       
       if success:
           actualizar_vista_playlist(id_playlist)
           mostrar_notificacion(message)
       else:
           mostrar_error(message)


3. TODAS LAS FUNCIONES RETORNAN:
   - Tuplas con (success, message, [datos])
   - success: bool - si la operación fue exitosa
   - message: str - mensaje para mostrar al usuario
   - datos: opcional - los datos resultantes


4. FUNCIONES PRINCIPALES DISPONIBLES:
   
   PLAYLISTS:
   - controller.create_new_playlist(nombre, desc, publica)
   - controller.list_my_playlists()  
   - controller.list_all_playlists()
   - controller.get_playlist_details(id_playlist)
   - controller.modify_playlist(id_playlist, nombre, desc, publica)
   - controller.remove_playlist(id_playlist)
   
   CANCIONES EN PLAYLISTS:
   - controller.add_song_to_playlist_by_id(id_playlist, id_cancion)
   - controller.remove_song_from_playlist_by_id(id_playlist, id_cancion)
   - controller.view_playlist_songs(id_playlist)
   - controller.move_song_in_playlist(id_playlist, id_cancion, nueva_pos)
   
   BÚSQUEDA Y EXPLORACIÓN:
   - controller.list_all_songs()
   - controller.search_songs_by_query(query)
   - controller.get_playlist_summary(id_playlist)
"""


# ==================== EJECUTAR DEMOSTRACIÓN ====================

if __name__ == "__main__":
    print("\n[MUSIC] Sistema de Gestión de Playlists - Ejemplos de Uso\n")
    
    respuesta = input("¿Deseas ejecutar la demostración completa? (s/n): ").strip().lower()
    
    if respuesta == 's':
        ejecutar_todos_los_ejemplos()
    else:
        print("\n[BOOKS] Revisa los ejemplos en el código para ver cómo usar cada función.")
        print("[TIP] Tip: Cada función está documentada y lista para usar en tu GUI.\n")
