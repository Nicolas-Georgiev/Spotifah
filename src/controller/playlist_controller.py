"""
Controlador para la gestión de playlists
Contiene la lógica de negocio y validaciones
"""
from typing import List, Dict, Optional, Tuple


class PlaylistController:
    def __init__(self, playlist_model):
        """
        Inicializa el controlador de playlists
        
        Args:
            playlist_model: Instancia de PlaylistModel
        """
        self.model = playlist_model
        self.current_user_id = 1  # Usuario por defecto (puedes cambiarlo según tu sistema)

    def set_current_user(self, id_usuario: int):
        """
        Establece el usuario actual
        
        Args:
            id_usuario: ID del usuario
        """
        self.current_user_id = id_usuario

    # ==================== GESTIÓN DE PLAYLISTS ====================

    def create_new_playlist(self, nombre: str, descripcion: str = "", publica: bool = False) -> Tuple[bool, str, Optional[int]]:
        """
        Crea una nueva playlist con validaciones
        
        Args:
            nombre: Nombre de la playlist
            descripcion: Descripción opcional
            publica: Si la playlist es pública
            
        Returns:
            Tupla (éxito, mensaje, id_playlist)
        """
        # Validaciones
        if not nombre or nombre.strip() == "":
            return False, "❌ El nombre de la playlist no puede estar vacío", None
        
        if len(nombre) > 100:
            return False, "❌ El nombre es demasiado largo (máximo 100 caracteres)", None
        
        # Crear playlist
        id_playlist = self.model.create_playlist(
            self.current_user_id, 
            nombre.strip(), 
            descripcion.strip(), 
            publica
        )
        
        if id_playlist:
            return True, f"✅ Playlist '{nombre}' creada correctamente (ID: {id_playlist})", id_playlist
        else:
            return False, "❌ Error al crear la playlist", None

    def list_my_playlists(self) -> Tuple[bool, str, List[Dict]]:
        """
        Lista todas las playlists del usuario actual
        
        Returns:
            Tupla (éxito, mensaje, lista_playlists)
        """
        playlists = self.model.get_all_playlists(self.current_user_id)
        
        if not playlists:
            return True, "ℹ️ No tienes playlists creadas", []
        
        return True, f"📋 Encontradas {len(playlists)} playlist(s)", playlists

    def list_all_playlists(self) -> Tuple[bool, str, List[Dict]]:
        """
        Lista todas las playlists del sistema
        
        Returns:
            Tupla (éxito, mensaje, lista_playlists)
        """
        playlists = self.model.get_all_playlists()
        
        if not playlists:
            return True, "ℹ️ No hay playlists en el sistema", []
        
        return True, f"📋 Encontradas {len(playlists)} playlist(s)", playlists

    def get_playlist_details(self, id_playlist: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Obtiene los detalles de una playlist
        
        Args:
            id_playlist: ID de la playlist
            
        Returns:
            Tupla (éxito, mensaje, datos_playlist)
        """
        playlist = self.model.get_playlist_by_id(id_playlist)
        
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}", None
        
        return True, "✅ Playlist encontrada", playlist

    def modify_playlist(self, id_playlist: int, nombre: Optional[str] = None, 
                       descripcion: Optional[str] = None, publica: Optional[bool] = None) -> Tuple[bool, str]:
        """
        Modifica una playlist existente
        
        Args:
            id_playlist: ID de la playlist
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            publica: Nueva visibilidad (opcional)
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar que la playlist existe
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}"
        
        # Validar nombre si se proporciona
        if nombre is not None:
            if nombre.strip() == "":
                return False, "❌ El nombre no puede estar vacío"
            if len(nombre) > 100:
                return False, "❌ El nombre es demasiado largo (máximo 100 caracteres)"
            nombre = nombre.strip()
        
        # Validar descripción si se proporciona
        if descripcion is not None:
            descripcion = descripcion.strip()
        
        # Actualizar
        success = self.model.update_playlist(id_playlist, nombre, descripcion, publica)
        
        if success:
            return True, "✅ Playlist actualizada correctamente"
        else:
            return False, "❌ Error al actualizar la playlist"

    def remove_playlist(self, id_playlist: int) -> Tuple[bool, str]:
        """
        Elimina una playlist
        
        Args:
            id_playlist: ID de la playlist a eliminar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar que la playlist existe
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}"
        
        # Eliminar
        success = self.model.delete_playlist(id_playlist)
        
        if success:
            return True, f"✅ Playlist '{playlist['nombre']}' eliminada correctamente"
        else:
            return False, "❌ Error al eliminar la playlist"

    # ==================== GESTIÓN DE CANCIONES EN PLAYLISTS ====================

    def add_song_to_playlist_by_id(self, id_playlist: int, id_cancion: int) -> Tuple[bool, str]:
        """
        Añade una canción a una playlist
        
        Args:
            id_playlist: ID de la playlist
            id_cancion: ID de la canción
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar que la playlist existe
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}"
        
        # Verificar que la canción existe
        cancion = self.model.get_song_by_id(id_cancion)
        if not cancion:
            return False, f"❌ No se encontró la canción con ID {id_cancion}"
        
        # Verificar que la canción no esté ya en la playlist
        canciones = self.model.get_playlist_songs(id_playlist)
        if any(c['id_cancion'] == id_cancion for c in canciones):
            return False, f"⚠️ La canción '{cancion['titulo']}' ya está en la playlist"
        
        # Añadir canción
        success = self.model.add_song_to_playlist(id_playlist, id_cancion)
        
        if success:
            return True, f"✅ Canción '{cancion['titulo']}' añadida a la playlist"
        else:
            return False, "❌ Error al añadir la canción a la playlist"

    def remove_song_from_playlist_by_id(self, id_playlist: int, id_cancion: int) -> Tuple[bool, str]:
        """
        Elimina una canción de una playlist
        
        Args:
            id_playlist: ID de la playlist
            id_cancion: ID de la canción
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar que la playlist existe
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}"
        
        # Verificar que la canción existe en la playlist
        canciones = self.model.get_playlist_songs(id_playlist)
        if not any(c['id_cancion'] == id_cancion for c in canciones):
            return False, "⚠️ La canción no está en esta playlist"
        
        # Eliminar canción
        success = self.model.remove_song_from_playlist(id_playlist, id_cancion)
        
        if success:
            return True, "✅ Canción eliminada de la playlist"
        else:
            return False, "❌ Error al eliminar la canción"

    def view_playlist_songs(self, id_playlist: int) -> Tuple[bool, str, List[Dict]]:
        """
        Obtiene las canciones de una playlist
        
        Args:
            id_playlist: ID de la playlist
            
        Returns:
            Tupla (éxito, mensaje, lista_canciones)
        """
        # Verificar que la playlist existe
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}", []
        
        # Obtener canciones
        canciones = self.model.get_playlist_songs(id_playlist)
        
        if not canciones:
            return True, f"ℹ️ La playlist '{playlist['nombre']}' está vacía", []
        
        return True, f"🎵 {len(canciones)} canción(es) en '{playlist['nombre']}'", canciones

    def move_song_in_playlist(self, id_playlist: int, id_cancion: int, nueva_posicion: int) -> Tuple[bool, str]:
        """
        Cambia la posición de una canción en la playlist
        
        Args:
            id_playlist: ID de la playlist
            id_cancion: ID de la canción
            nueva_posicion: Nueva posición (empezando desde 1)
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Verificar que la playlist existe
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}"
        
        # Verificar que la canción está en la playlist
        canciones = self.model.get_playlist_songs(id_playlist)
        if not any(c['id_cancion'] == id_cancion for c in canciones):
            return False, "⚠️ La canción no está en esta playlist"
        
        # Validar la nueva posición
        if nueva_posicion < 1 or nueva_posicion > len(canciones):
            return False, f"❌ Posición inválida. Debe estar entre 1 y {len(canciones)}"
        
        # Reordenar
        success = self.model.reorder_song_in_playlist(id_playlist, id_cancion, nueva_posicion)
        
        if success:
            return True, f"✅ Canción movida a la posición {nueva_posicion}"
        else:
            return False, "❌ Error al reordenar la canción"

    # ==================== BÚSQUEDA Y LISTADO DE CANCIONES ====================

    def list_all_songs(self) -> Tuple[bool, str, List[Dict]]:
        """
        Lista todas las canciones disponibles
        
        Returns:
            Tupla (éxito, mensaje, lista_canciones)
        """
        canciones = self.model.get_all_songs()
        
        if not canciones:
            return True, "ℹ️ No hay canciones en la base de datos", []
        
        return True, f"🎵 Encontradas {len(canciones)} canción(es)", canciones

    def search_songs_by_query(self, query: str) -> Tuple[bool, str, List[Dict]]:
        """
        Busca canciones por título, artista o álbum
        
        Args:
            query: Texto de búsqueda
            
        Returns:
            Tupla (éxito, mensaje, lista_canciones)
        """
        if not query or query.strip() == "":
            return False, "❌ Debes proporcionar un término de búsqueda", []
        
        canciones = self.model.search_songs(query.strip())
        
        if not canciones:
            return True, f"ℹ️ No se encontraron canciones con '{query}'", []
        
        return True, f"🔍 Encontradas {len(canciones)} canción(es) con '{query}'", canciones

    # ==================== UTILIDADES ====================

    def get_playlist_summary(self, id_playlist: int) -> Tuple[bool, str, Optional[Dict]]:
        """
        Obtiene un resumen completo de la playlist (info + canciones)
        
        Args:
            id_playlist: ID de la playlist
            
        Returns:
            Tupla (éxito, mensaje, datos_resumen)
        """
        # Obtener información de la playlist
        playlist = self.model.get_playlist_by_id(id_playlist)
        if not playlist:
            return False, f"❌ No se encontró la playlist con ID {id_playlist}", None
        
        # Obtener canciones
        canciones = self.model.get_playlist_songs(id_playlist)
        
        # Calcular duración total
        duracion_total = sum(c.get('duracion_seg', 0) for c in canciones)
        
        resumen = {
            'playlist': playlist,
            'canciones': canciones,
            'total_canciones': len(canciones),
            'duracion_total_seg': duracion_total,
            'duracion_total_min': duracion_total // 60
        }
        
        return True, "✅ Resumen generado", resumen
