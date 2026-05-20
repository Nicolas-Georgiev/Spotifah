"""
Modelo para la gestión de playlists
Contiene todas las operaciones de base de datos relacionadas con playlists
"""
import sqlite3
from typing import List, Dict, Optional, Tuple


class PlaylistModel:
    def __init__(self, db):
        """
        Inicializa el modelo de playlist
        
        Args:
            db: Instancia de Database (del módulo databaseManager.db)
        """
        self.db = db

    # ==================== OPERACIONES CON PLAYLISTS ====================
    
    def create_playlist(self, id_usuario: int, nombre: str, descripcion: str = "", publica: bool = False) -> Optional[int]:
        """
        Crea una nueva playlist
        
        Args:
            id_usuario: ID del usuario propietario
            nombre: Nombre de la playlist
            descripcion: Descripción opcional
            publica: Si la playlist es pública o privada
            
        Returns:
            ID de la playlist creada o None si hay error
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO playlists (id_usuario, nombre, descripcion, publica)
                VALUES (?, ?, ?, ?)
            """, (id_usuario, nombre, descripcion, 1 if publica else 0))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error al crear playlist: {e}")
            return None
        finally:
            conn.close()

    def get_all_playlists(self, id_usuario: Optional[int] = None) -> List[Dict]:
        """
        Obtiene todas las playlists (opcionalmente filtradas por usuario)
        
        Args:
            id_usuario: Si se especifica, filtra por este usuario
            
        Returns:
            Lista de diccionarios con información de playlists
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            if id_usuario:
                cursor.execute("""
                    SELECT p.*, u.nombre_usuario,
                           (SELECT COUNT(*) FROM playlist_canciones pc WHERE pc.id_playlist = p.id_playlist) as total_canciones
                    FROM playlists p
                    JOIN usuarios u ON p.id_usuario = u.id_usuario
                    WHERE p.id_usuario = ?
                    ORDER BY p.fecha_creacion DESC
                """, (id_usuario,))
            else:
                cursor.execute("""
                    SELECT p.*, u.nombre_usuario,
                           (SELECT COUNT(*) FROM playlist_canciones pc WHERE pc.id_playlist = p.id_playlist) as total_canciones
                    FROM playlists p
                    JOIN usuarios u ON p.id_usuario = u.id_usuario
                    ORDER BY p.fecha_creacion DESC
                """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error al obtener playlists: {e}")
            return []
        finally:
            conn.close()

    def get_playlist_by_id(self, id_playlist: int) -> Optional[Dict]:
        """
        Obtiene información de una playlist específica
        
        Args:
            id_playlist: ID de la playlist
            
        Returns:
            Diccionario con información de la playlist o None
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, u.nombre_usuario,
                       (SELECT COUNT(*) FROM playlist_canciones pc WHERE pc.id_playlist = p.id_playlist) as total_canciones
                FROM playlists p
                JOIN usuarios u ON p.id_usuario = u.id_usuario
                WHERE p.id_playlist = ?
            """, (id_playlist,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error al obtener playlist: {e}")
            return None
        finally:
            conn.close()

    def update_playlist(self, id_playlist: int, nombre: Optional[str] = None, 
                       descripcion: Optional[str] = None, publica: Optional[bool] = None) -> bool:
        """
        Actualiza información de una playlist
        
        Args:
            id_playlist: ID de la playlist a actualizar
            nombre: Nuevo nombre (opcional)
            descripcion: Nueva descripción (opcional)
            publica: Nueva visibilidad (opcional)
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        conn = self.db.get_connection()
        try:
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
            
            if not updates:
                return True
            
            params.append(id_playlist)
            query = f"UPDATE playlists SET {', '.join(updates)} WHERE id_playlist = ?"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar playlist: {e}")
            return False
        finally:
            conn.close()

    def delete_playlist(self, id_playlist: int) -> bool:
        """
        Elimina una playlist (CASCADE eliminará automáticamente las relaciones)
        
        Args:
            id_playlist: ID de la playlist a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM playlists WHERE id_playlist = ?", (id_playlist,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar playlist: {e}")
            return False
        finally:
            conn.close()

    # ==================== OPERACIONES CON CANCIONES EN PLAYLISTS ====================

    def add_song_to_playlist(self, id_playlist: int, id_cancion: int, orden: Optional[int] = None) -> bool:
        """
        Añade una canción a una playlist
        
        Args:
            id_playlist: ID de la playlist
            id_cancion: ID de la canción a añadir
            orden: Posición en la playlist (si no se especifica, se añade al final)
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            
            # Si no se especifica orden, obtener el siguiente
            if orden is None:
                cursor.execute("""
                    SELECT COALESCE(MAX(orden), 0) + 1 as next_orden
                    FROM playlist_canciones
                    WHERE id_playlist = ?
                """, (id_playlist,))
                result = cursor.fetchone()
                orden = result['next_orden']
            
            cursor.execute("""
                INSERT OR IGNORE INTO playlist_canciones (id_playlist, id_cancion, orden)
                VALUES (?, ?, ?)
            """, (id_playlist, id_cancion, orden))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al añadir canción a playlist: {e}")
            return False
        finally:
            conn.close()

    def remove_song_from_playlist(self, id_playlist: int, id_cancion: int) -> bool:
        """
        Elimina una canción de una playlist
        
        Args:
            id_playlist: ID de la playlist
            id_cancion: ID de la canción a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM playlist_canciones
                WHERE id_playlist = ? AND id_cancion = ?
            """, (id_playlist, id_cancion))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar canción de playlist: {e}")
            return False
        finally:
            conn.close()

    def get_playlist_songs(self, id_playlist: int) -> List[Dict]:
        """
        Obtiene todas las canciones de una playlist ordenadas por su posición
        
        Args:
            id_playlist: ID de la playlist
            
        Returns:
            Lista de diccionarios con información de canciones
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, pc.orden
                FROM canciones c
                JOIN playlist_canciones pc ON c.id_cancion = pc.id_cancion
                WHERE pc.id_playlist = ?
                ORDER BY pc.orden ASC
            """, (id_playlist,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error al obtener canciones de playlist: {e}")
            return []
        finally:
            conn.close()

    def reorder_song_in_playlist(self, id_playlist: int, id_cancion: int, nuevo_orden: int) -> bool:
        """
        Cambia el orden de una canción en la playlist
        
        Args:
            id_playlist: ID de la playlist
            id_cancion: ID de la canción a reordenar
            nuevo_orden: Nueva posición
            
        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE playlist_canciones
                SET orden = ?
                WHERE id_playlist = ? AND id_cancion = ?
            """, (nuevo_orden, id_playlist, id_cancion))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al reordenar canción: {e}")
            return False
        finally:
            conn.close()

    # ==================== OPERACIONES CON CANCIONES ====================

    def get_all_songs(self) -> List[Dict]:
        """
        Obtiene todas las canciones disponibles en la base de datos
        
        Returns:
            Lista de diccionarios con información de canciones
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM canciones
                ORDER BY titulo ASC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error al obtener canciones: {e}")
            return []
        finally:
            conn.close()

    def search_songs(self, query: str) -> List[Dict]:
        """
        Busca canciones por título, artista o álbum
        
        Args:
            query: Texto de búsqueda
            
        Returns:
            Lista de diccionarios con canciones que coinciden
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT * FROM canciones
                WHERE titulo LIKE ? OR artista LIKE ? OR album LIKE ?
                ORDER BY titulo ASC
            """, (search_pattern, search_pattern, search_pattern))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error al buscar canciones: {e}")
            return []
        finally:
            conn.close()

    def get_song_by_id(self, id_cancion: int) -> Optional[Dict]:
        """
        Obtiene información de una canción específica
        
        Args:
            id_cancion: ID de la canción
            
        Returns:
            Diccionario con información de la canción o None
        """
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM canciones WHERE id_cancion = ?", (id_cancion,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error al obtener canción: {e}")
            return None
        finally:
            conn.close()
