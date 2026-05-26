"""
Vista de terminal para la gestión de playlists
Interfaz de línea de comandos interactiva
"""
from typing import Optional
import os


class PlaylistView:
    def __init__(self, controller):
        """
        Inicializa la vista de playlists
        
        Args:
            controller: Instancia de PlaylistController
        """
        self.controller = controller

    # ==================== UTILIDADES DE VISUALIZACIÓN ====================

    def clear_screen(self):
        """Limpia la pantalla (compatible con Windows)"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str):
        """Imprime un encabezado formateado"""
        print("\n" + "=" * 60)
        print(f"  {title}")
        print("=" * 60)

    def print_separator(self):
        """Imprime una línea separadora"""
        print("-" * 60)

    def wait_for_key(self):
        """Espera a que el usuario presione Enter"""
        input("\n[Presiona Enter para continuar...]")

    def format_duration(self, seconds: int) -> str:
        """Formatea duración en segundos a formato MM:SS"""
        if seconds is None or seconds == 0:
            return "0:00"
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"

    # ==================== VISUALIZACIÓN DE PLAYLISTS ====================

    def display_playlist(self, playlist: dict, detailed: bool = False):
        """
        Muestra información de una playlist
        
        Args:
            playlist: Diccionario con datos de la playlist
            detailed: Si True, muestra información detallada
        """
        visibilidad = "[GLOBE] Pública" if playlist.get('publica', 0) == 1 else "[LOCK] Privada"
        canciones = playlist.get('total_canciones', 0)
        
        print(f"\n[LIST] [{playlist['id_playlist']}] {playlist['nombre']}")
        print(f"   [USER] Por: {playlist.get('nombre_usuario', 'Desconocido')}")
        print(f"   [MUSIC] Canciones: {canciones} | {visibilidad}")
        
        if detailed:
            descripcion = playlist.get('descripcion', '')
            if descripcion:
                print(f"   [NOTE] {descripcion}")
            fecha = playlist.get('fecha_creacion', '')
            if fecha:
                print(f"   [DATE] Creada: {fecha}")

    def display_playlists_list(self, playlists: list):
        """Muestra una lista de playlists"""
        if not playlists:
            print("\n[INFO] No hay playlists para mostrar")
            return
        
        for playlist in playlists:
            self.display_playlist(playlist)

    def display_song(self, song: dict, show_order: bool = False):
        """
        Muestra información de una canción
        
        Args:
            song: Diccionario con datos de la canción
            show_order: Si True, muestra el orden en la playlist
        """
        orden_str = f"[{song['orden']}] " if show_order and 'orden' in song else ""
        titulo = song.get('titulo', 'Sin título')
        artista = song.get('artista', 'Desconocido')
        duracion = self.format_duration(song.get('duracion_seg', 0))
        album = song.get('album', '')
        genero = song.get('genero', '')
        
        print(f"\n   [MUSIC] {orden_str}[{song['id_cancion']}] {titulo}")
        print(f"      [USER] {artista} | [TIMER] {duracion}", end='')
        
        if album:
            print(f" | [DISC] {album}", end='')
        if genero:
            print(f" | [GUITAR] {genero}", end='')
        print()

    def display_songs_list(self, songs: list, show_order: bool = False):
        """Muestra una lista de canciones"""
        if not songs:
            print("\n[INFO] No hay canciones para mostrar")
            return
        
        for song in songs:
            self.display_song(song, show_order)

    def display_playlist_summary(self, summary: dict):
        """Muestra un resumen completo de una playlist"""
        playlist = summary['playlist']
        canciones = summary['canciones']
        
        self.print_header(f"[LIST] {playlist['nombre']}")
        
        print(f"\n[USER] Creador: {playlist.get('nombre_usuario', 'Desconocido')}")
        descripcion = playlist.get('descripcion', '')
        if descripcion:
            print(f"[NOTE] Descripción: {descripcion}")
        
        visibilidad = "[GLOBE] Pública" if playlist.get('publica', 0) == 1 else "[LOCK] Privada"
        print(f"[VIEW] Visibilidad: {visibilidad}")
        
        print(f"\n[CHART] Estadísticas:")
        print(f"   [MUSIC] Total de canciones: {summary['total_canciones']}")
        print(f"   [TIMER] Duración total: {summary['duracion_total_min']} min ({summary['duracion_total_seg']} seg)")
        
        if canciones:
            print(f"\n[MUSIC] Canciones:")
            self.display_songs_list(canciones, show_order=True)

    # ==================== MENÚS PRINCIPALES ====================

    def show_main_menu(self) -> Optional[str]:
        """
        Muestra el menú principal
        
        Returns:
            Opción seleccionada por el usuario
        """
        self.clear_screen()
        self.print_header("[MUSIC] GESTOR DE PLAYLISTS [MUSIC]")
        
        print("\n[PLAYLISTS]")
        print("  1. [LIST] Ver mis playlists")
        print("  2. [PLUS] Crear nueva playlist")
        print("  3. [EDIT]  Editar playlist")
        print("  4. [TRASH]  Eliminar playlist")
        
        print("\n[CANCIONES]")
        print("  5. [MUSIC] Ver canciones de una playlist")
        print("  6. [PLUS] Añadir canción a playlist")
        print("  7. [MINUS] Eliminar canción de playlist")
        print("  8. [SHUFFLE] Reordenar canción en playlist")
        
        print("\n[EXPLORAR]")
        print("  9. [SEARCH] Buscar canciones")
        print(" 10. [SCROLL] Ver todas las canciones")
        
        print("\n  0. [DOOR] Salir")
        
        self.print_separator()
        return input("\n[POINT] Selecciona una opción: ").strip()

    # ==================== OPERACIONES CON PLAYLISTS ====================

    def view_my_playlists(self):
        """Muestra las playlists del usuario"""
        self.clear_screen()
        self.print_header("[LIST] MIS PLAYLISTS")
        
        success, message, playlists = self.controller.list_my_playlists()
        print(f"\n{message}")
        
        if playlists:
            self.display_playlists_list(playlists)
        
        self.wait_for_key()

    def create_playlist(self):
        """Interfaz para crear una nueva playlist"""
        self.clear_screen()
        self.print_header("[PLUS] CREAR NUEVA PLAYLIST")
        
        print("\n")
        nombre = input("[NOTE] Nombre de la playlist: ").strip()
        if not nombre:
            print("[ERR] Operación cancelada")
            self.wait_for_key()
            return
        
        descripcion = input("[FILE] Descripción (opcional): ").strip()
        
        publica_input = input("[GLOBE] ¿Hacer pública? (s/N): ").strip().lower()
        publica = publica_input == 's'
        
        print("\n[SAND] Creando playlist...")
        success, message, id_playlist = self.controller.create_new_playlist(nombre, descripcion, publica)
        print(f"\n{message}")
        
        self.wait_for_key()

    def edit_playlist(self):
        """Interfaz para editar una playlist"""
        self.clear_screen()
        self.print_header("[EDIT] EDITAR PLAYLIST")
        
        # Mostrar playlists del usuario
        success, message, playlists = self.controller.list_my_playlists()
        if playlists:
            self.display_playlists_list(playlists)
        else:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        print("\n")
        id_playlist = input("[NUM] ID de la playlist a editar (Enter para cancelar): ").strip()
        if not id_playlist:
            return
        
        try:
            id_playlist = int(id_playlist)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Obtener datos actuales
        success, msg, playlist = self.controller.get_playlist_details(id_playlist)
        if not success:
            print(f"\n{msg}")
            self.wait_for_key()
            return
        
        print(f"\n[LIST] Editando: {playlist['nombre']}")
        print("(Dejar en blanco para mantener el valor actual)\n")
        
        nuevo_nombre = input(f"[NOTE] Nuevo nombre [{playlist['nombre']}]: ").strip()
        nueva_desc = input(f"[FILE] Nueva descripción [{playlist.get('descripcion', '')}]: ").strip()
        
        publica_actual = "Sí" if playlist.get('publica', 0) == 1 else "No"
        publica_input = input(f"[GLOBE] ¿Pública? (s/n) [{publica_actual}]: ").strip().lower()
        
        nueva_publica = None
        if publica_input == 's':
            nueva_publica = True
        elif publica_input == 'n':
            nueva_publica = False
        
        # Aplicar cambios
        success, message = self.controller.modify_playlist(
            id_playlist,
            nuevo_nombre if nuevo_nombre else None,
            nueva_desc if nueva_desc else None,
            nueva_publica
        )
        
        print(f"\n{message}")
        self.wait_for_key()

    def delete_playlist(self):
        """Interfaz para eliminar una playlist"""
        self.clear_screen()
        self.print_header("[TRASH] ELIMINAR PLAYLIST")
        
        # Mostrar playlists del usuario
        success, message, playlists = self.controller.list_my_playlists()
        if playlists:
            self.display_playlists_list(playlists)
        else:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        print("\n")
        id_playlist = input("[NUM] ID de la playlist a eliminar (Enter para cancelar): ").strip()
        if not id_playlist:
            return
        
        try:
            id_playlist = int(id_playlist)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Confirmar
        confirmacion = input(f"\n[WARN] ¿Seguro que quieres eliminar la playlist? (s/N): ").strip().lower()
        if confirmacion != 's':
            print("[ERR] Operación cancelada")
            self.wait_for_key()
            return
        
        # Eliminar
        success, message = self.controller.remove_playlist(id_playlist)
        print(f"\n{message}")
        self.wait_for_key()

    # ==================== OPERACIONES CON CANCIONES EN PLAYLISTS ====================

    def view_playlist_songs(self):
        """Muestra las canciones de una playlist"""
        self.clear_screen()
        self.print_header("[MUSIC] CANCIONES DE PLAYLIST")
        
        # Mostrar playlists del usuario
        success, message, playlists = self.controller.list_my_playlists()
        if playlists:
            self.display_playlists_list(playlists)
        else:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        print("\n")
        id_playlist = input("[NUM] ID de la playlist (Enter para cancelar): ").strip()
        if not id_playlist:
            return
        
        try:
            id_playlist = int(id_playlist)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Obtener resumen completo
        self.clear_screen()
        success, message, summary = self.controller.get_playlist_summary(id_playlist)
        
        if success:
            self.display_playlist_summary(summary)
        else:
            print(f"\n{message}")
        
        self.wait_for_key()

    def add_song_to_playlist(self):
        """Interfaz para añadir una canción a una playlist"""
        self.clear_screen()
        self.print_header("[PLUS] AÑADIR CANCIÓN A PLAYLIST")
        
        # Mostrar playlists
        success, message, playlists = self.controller.list_my_playlists()
        if playlists:
            self.display_playlists_list(playlists)
        else:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        print("\n")
        id_playlist = input("[NUM] ID de la playlist (Enter para cancelar): ").strip()
        if not id_playlist:
            return
        
        try:
            id_playlist = int(id_playlist)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Mostrar canciones disponibles
        self.clear_screen()
        self.print_header("[MUSIC] CANCIONES DISPONIBLES")
        
        success, message, canciones = self.controller.list_all_songs()
        print(f"\n{message}")
        
        if canciones:
            self.display_songs_list(canciones)
        else:
            self.wait_for_key()
            return
        
        print("\n")
        id_cancion = input("[NUM] ID de la canción a añadir (Enter para cancelar): ").strip()
        if not id_cancion:
            return
        
        try:
            id_cancion = int(id_cancion)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Añadir canción
        success, message = self.controller.add_song_to_playlist_by_id(id_playlist, id_cancion)
        print(f"\n{message}")
        self.wait_for_key()

    def remove_song_from_playlist(self):
        """Interfaz para eliminar una canción de una playlist"""
        self.clear_screen()
        self.print_header("[MINUS] ELIMINAR CANCIÓN DE PLAYLIST")
        
        # Mostrar playlists
        success, message, playlists = self.controller.list_my_playlists()
        if playlists:
            self.display_playlists_list(playlists)
        else:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        print("\n")
        id_playlist = input("[NUM] ID de la playlist (Enter para cancelar): ").strip()
        if not id_playlist:
            return
        
        try:
            id_playlist = int(id_playlist)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Mostrar canciones de la playlist
        self.clear_screen()
        success, message, canciones = self.controller.view_playlist_songs(id_playlist)
        
        if not success:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        self.print_header("[MUSIC] CANCIONES EN LA PLAYLIST")
        print(f"\n{message}")
        
        if canciones:
            self.display_songs_list(canciones, show_order=True)
        else:
            self.wait_for_key()
            return
        
        print("\n")
        id_cancion = input("[NUM] ID de la canción a eliminar (Enter para cancelar): ").strip()
        if not id_cancion:
            return
        
        try:
            id_cancion = int(id_cancion)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Eliminar canción
        success, message = self.controller.remove_song_from_playlist_by_id(id_playlist, id_cancion)
        print(f"\n{message}")
        self.wait_for_key()

    def reorder_song_in_playlist(self):
        """Interfaz para reordenar una canción en una playlist"""
        self.clear_screen()
        self.print_header("[SHUFFLE] REORDENAR CANCIÓN EN PLAYLIST")
        
        # Mostrar playlists
        success, message, playlists = self.controller.list_my_playlists()
        if playlists:
            self.display_playlists_list(playlists)
        else:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        print("\n")
        id_playlist = input("[NUM] ID de la playlist (Enter para cancelar): ").strip()
        if not id_playlist:
            return
        
        try:
            id_playlist = int(id_playlist)
        except ValueError:
            print("[ERR] ID inválido")
            self.wait_for_key()
            return
        
        # Mostrar canciones de la playlist
        self.clear_screen()
        success, message, canciones = self.controller.view_playlist_songs(id_playlist)
        
        if not success:
            print(f"\n{message}")
            self.wait_for_key()
            return
        
        self.print_header("[MUSIC] CANCIONES EN LA PLAYLIST")
        print(f"\n{message}")
        
        if canciones:
            self.display_songs_list(canciones, show_order=True)
        else:
            self.wait_for_key()
            return
        
        print("\n")
        id_cancion = input("[NUM] ID de la canción a mover (Enter para cancelar): ").strip()
        if not id_cancion:
            return
        
        nueva_pos = input("[PIN] Nueva posición: ").strip()
        if not nueva_pos:
            return
        
        try:
            id_cancion = int(id_cancion)
            nueva_pos = int(nueva_pos)
        except ValueError:
            print("[ERR] Valores inválidos")
            self.wait_for_key()
            return
        
        # Reordenar
        success, message = self.controller.move_song_in_playlist(id_playlist, id_cancion, nueva_pos)
        print(f"\n{message}")
        self.wait_for_key()

    # ==================== EXPLORACIÓN DE CANCIONES ====================

    def search_songs(self):
        """Interfaz para buscar canciones"""
        self.clear_screen()
        self.print_header("[SEARCH] BUSCAR CANCIONES")
        
        print("\n")
        query = input("[SEARCH] Buscar por título, artista o álbum: ").strip()
        if not query:
            return
        
        print("\n[SAND] Buscando...")
        success, message, canciones = self.controller.search_songs_by_query(query)
        
        print(f"\n{message}")
        if canciones:
            self.display_songs_list(canciones)
        
        self.wait_for_key()

    def view_all_songs(self):
        """Muestra todas las canciones disponibles"""
        self.clear_screen()
        self.print_header("[SCROLL] TODAS LAS CANCIONES")
        
        success, message, canciones = self.controller.list_all_songs()
        print(f"\n{message}")
        
        if canciones:
            self.display_songs_list(canciones)
        
        self.wait_for_key()

    # ==================== BUCLE PRINCIPAL ====================

    def run(self):
        """Ejecuta el bucle principal de la interfaz"""
        menu_options = {
            '1': self.view_my_playlists,
            '2': self.create_playlist,
            '3': self.edit_playlist,
            '4': self.delete_playlist,
            '5': self.view_playlist_songs,
            '6': self.add_song_to_playlist,
            '7': self.remove_song_from_playlist,
            '8': self.reorder_song_in_playlist,
            '9': self.search_songs,
            '10': self.view_all_songs,
        }
        
        while True:
            option = self.show_main_menu()
            
            if option == '0':
                self.clear_screen()
                print("\n[HELLO] ¡Hasta pronto!\n")
                break
            
            if option in menu_options:
                try:
                    menu_options[option]()
                except Exception as e:
                    print(f"\n[ERR] Error: {e}")
                    self.wait_for_key()
            else:
                print("\n[ERR] Opción inválida")
                self.wait_for_key()
