import os
import stat

from api.covers import CoversMixin


class PlaylistsMixin(CoversMixin):
    def get_playlists(self) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id_playlist, nombre, descripcion, publica FROM playlists ORDER BY id_playlist"
                )
                playlists = []
                for row in cur.fetchall():
                    pid = str(row["id_playlist"])
                    cover = self._playlist_cover_url(row["id_playlist"])
                    if not cover and row["nombre"] == "Favoritos":
                        cover = "/portadas/favorites.svg"
                    playlists.append({
                        "id": pid,
                        "name": row["nombre"],
                        "description": row["descripcion"] or "",
                        "is_public": bool(row["publica"]),
                        "cover_url": cover,
                    })
                playlists.insert(0, {
                    "id": "all",
                    "name": "Todas mis canciones",
                    "description": "Todas las canciones en tu biblioteca",
                    "is_public": False,
                    "cover_url": "/portadas/all-songs.svg",
                })
                return playlists
            finally:
                conn.close()
        except Exception:
            return [{
                "id": "all",
                "name": "Todas mis canciones",
                "description": "",
                "is_public": False,
                "cover_url": "/portadas/all-songs.svg",
            }]

    def get_playlist_songs(self, playlist_id: str) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                if playlist_id == "all":
                    cur.execute("""
                        SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                               c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url,
                               d.fecha_descarga
                        FROM canciones c
                        LEFT JOIN (
                            SELECT id_cancion, MAX(fecha_descarga) as fecha_descarga
                            FROM descargas GROUP BY id_cancion
                        ) d ON c.id_cancion = d.id_cancion
                        ORDER BY c.titulo
                    """)
                else:
                    cur.execute("""
                        SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                               c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url,
                               d.fecha_descarga
                        FROM playlist_canciones pc
                        JOIN canciones c ON pc.id_cancion = c.id_cancion
                        LEFT JOIN (
                            SELECT id_cancion, MAX(fecha_descarga) as fecha_descarga
                            FROM descargas GROUP BY id_cancion
                        ) d ON c.id_cancion = d.id_cancion
                        WHERE pc.id_playlist = ?
                        ORDER BY pc.orden
                    """, (int(playlist_id),))
                rows = cur.fetchall()
                result = []
                for row in rows:
                    song_id = row["id_cancion"]
                    cover_url = row["caratula_url"] or ""
                    if not cover_url:
                        cover_url = self._ensure_cover(
                            song_id=song_id,
                            title=row["titulo"],
                            artist=row["artista"] or "",
                            album=row["album"] or "",
                            mp3_path=row["ruta_local"] or "",
                            plataforma=row["plataforma_origen"] or "",
                        )
                    cover_url = self._localize_cover(song_id, cover_url)
                    fecha_descarga = row["fecha_descarga"] or ""
                    is_downloaded = bool(fecha_descarga) and os.path.exists(row["ruta_local"] or "")
                    result.append({
                        "id": str(song_id),
                        "title": row["titulo"],
                        "artist": row["artista"] or "",
                        "album": row["album"] or "",
                        "duration": row["duracion_seg"] or 0,
                        "genre": row["genero"] or "",
                        "source": row["plataforma_origen"] or "",
                        "path": row["ruta_local"] or "",
                        "cover_url": cover_url,
                        "is_downloaded": is_downloaded,
                        "download_date": fecha_descarga,
                    })
                return result
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_songs(self) -> list:
        return self.get_playlist_songs("all")

    def add_song_to_playlist(self, playlist_id: str, song_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (int(playlist_id), int(song_id)),
                )
                already = cur.fetchone() is not None
                if already:
                    return {
                        "ok": True,
                        "data": {"message": "La cancion ya esta en la playlist", "already_exists": True},
                    }
                cur.execute(
                    "SELECT COALESCE(MAX(orden), 0) + 1 FROM playlist_canciones WHERE id_playlist = ?",
                    (int(playlist_id),),
                )
                next_order = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO playlist_canciones (id_playlist, id_cancion, orden) VALUES (?, ?, ?)",
                    (int(playlist_id), int(song_id), next_order),
                )
                conn.commit()
                return {
                    "ok": True,
                    "data": {"message": "Cancion anadida a la playlist", "already_exists": False},
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def remove_song_from_playlist(self, playlist_id: str, song_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (int(playlist_id), int(song_id)),
                )
                conn.commit()
                return {"ok": True, "data": {"message": "Cancion eliminada de la playlist"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_song(self, song_id: str) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT ruta_local FROM canciones WHERE id_cancion = ?", (int(song_id),))
                row = cur.fetchone()
                file_path = row["ruta_local"] if row else None

                deleted = False
                if file_path:
                    if os.path.exists(file_path):
                        try:
                            os.chmod(file_path, stat.S_IWRITE)
                            os.remove(file_path)
                            deleted = True
                        except Exception as e:
                            print(f"delete_song: no se pudo eliminar {file_path}: {e}")

                    if not deleted:
                        filename = os.path.basename(file_path)
                        alt_path = os.path.join(self._music_dir, filename)
                        if alt_path != file_path and os.path.exists(alt_path):
                            try:
                                os.chmod(alt_path, stat.S_IWRITE)
                                os.remove(alt_path)
                                deleted = True
                            except Exception as e:
                                print(f"delete_song: fallback tampoco funciono para {alt_path}: {e}")

                cur.execute("DELETE FROM playlist_canciones WHERE id_cancion = ?", (int(song_id),))
                cur.execute("DELETE FROM historial_reproduccion WHERE id_cancion = ?", (int(song_id),))
                cur.execute("DELETE FROM canciones WHERE id_cancion = ?", (int(song_id),))
                conn.commit()

                if self._music_controller:
                    self._music_controller.remove_from_queue(int(song_id))

                return {"ok": True, "data": {"message": "Cancion eliminada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def update_song(self, song_id: str, data: dict) -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                updates = []
                params = []
                field_mapping = {
                    "title": "titulo",
                    "artist": "artista",
                    "album": "album",
                    "genre": "genero",
                }
                for frontend_field, db_column in field_mapping.items():
                    if frontend_field in data:
                        updates.append(f"{db_column} = ?")
                        params.append(data[frontend_field].strip())
                if "cover_base64" in data and data["cover_base64"]:
                    import base64
                    cover_data = data["cover_base64"]
                    if "," in cover_data:
                        cover_data = cover_data.split(",")[1]
                    cover_blob = base64.b64decode(cover_data)
                    updates.append("caratula_blob = ?")
                    params.append(cover_blob)
                    local_url = f"/api/covers/{int(song_id)}.jpg"
                    updates.append("caratula_url = ?")
                    params.append(local_url)
                if not updates:
                    return {"ok": False, "error": "No hay campos para actualizar"}
                params.append(int(song_id))
                cur.execute(
                    f"UPDATE canciones SET {', '.join(updates)} WHERE id_cancion = ?",
                    params,
                )
                conn.commit()
                return {"ok": True, "data": {"message": "Canción actualizada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def create_playlist(self, name: str, description: str = "") -> dict:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO playlists (id_usuario, nombre, descripcion, publica) VALUES (?, ?, ?, ?)",
                    (1, name.strip(), description.strip(), 0),
                )
                conn.commit()
                new_id = cur.lastrowid
                return {
                    "ok": True,
                    "data": {
                        "id": str(new_id),
                        "name": name.strip(),
                        "description": description.strip(),
                        "is_public": False,
                    },
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def delete_playlist(self, playlist_id: str) -> dict:
        if playlist_id == "all":
            return {"ok": False, "error": "No se puede eliminar esta playlist"}
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM playlists WHERE id_playlist = ?", (int(playlist_id),))
                row = cur.fetchone()
                if not row:
                    return {"ok": False, "error": "Playlist no encontrada"}
                if row["nombre"] == "Favoritos":
                    return {"ok": False, "error": "No se puede eliminar la playlist de favoritos"}
                cur.execute("DELETE FROM playlists WHERE id_playlist = ?", (int(playlist_id),))
                conn.commit()
                return {"ok": True, "data": {"message": "Playlist eliminada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def rename_playlist(self, playlist_id: str, name: str, description: str = "", cover_base64: str = None) -> dict:
        if playlist_id == "all":
            return {"ok": False, "error": "No se puede renombrar esta playlist"}
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT nombre FROM playlists WHERE id_playlist = ?", (int(playlist_id),))
                row = cur.fetchone()
                if not row:
                    return {"ok": False, "error": "Playlist no encontrada"}
                if row["nombre"] == "Favoritos":
                    return {"ok": False, "error": "No se puede renombrar la playlist de favoritos"}
                import base64
                updates = ["nombre = ?", "descripcion = ?"]
                params = [name.strip(), description.strip()]
                if cover_base64:
                    cover_data = cover_base64
                    if "," in cover_data:
                        cover_data = cover_data.split(",")[1]
                    cover_blob = base64.b64decode(cover_data)
                    updates.append("caratula_blob = ?")
                    params.append(cover_blob)
                params.append(int(playlist_id))
                cur.execute(
                    f"UPDATE playlists SET {', '.join(updates)} WHERE id_playlist = ?",
                    params,
                )
                conn.commit()
                return {"ok": True, "data": {"message": "Playlist actualizada"}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def search_songs(self, query: str) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                pattern = f"%{query}%"
                cur.execute("""
                    SELECT id_cancion, titulo, artista, album, duracion_seg,
                           genero, plataforma_origen, ruta_local, caratula_url
                    FROM canciones
                    WHERE titulo LIKE ? OR artista LIKE ? OR album LIKE ?
                    ORDER BY titulo LIMIT 50
                """, (pattern, pattern, pattern))
                rows = cur.fetchall()
                result = []
                for row in rows:
                    sid = row["id_cancion"]
                    cover = row["caratula_url"] or ""
                    if not cover:
                        cover = self._ensure_cover(sid, row["titulo"], row["artista"] or "", row["album"] or "", row["ruta_local"] or "", row["plataforma_origen"] or "")
                    cover = self._localize_cover(sid, cover)
                    result.append({
                        "id": str(sid),
                        "title": row["titulo"],
                        "artist": row["artista"] or "",
                        "album": row["album"] or "",
                        "duration": row["duracion_seg"] or 0,
                        "genre": row["genero"] or "",
                        "source": row["plataforma_origen"] or "",
                        "path": row["ruta_local"] or "",
                        "cover_url": cover,
                    })
                return result
            finally:
                conn.close()
        except Exception:
            return []

    def toggle_favorite(self, song_id: str) -> dict:
        try:
            fav_id = self._ensure_favorites_playlist()
            if not fav_id:
                return {"ok": False, "error": "No se pudo obtener la playlist de favoritos"}
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (fav_id, int(song_id)),
                )
                is_fav = cur.fetchone() is not None
                if is_fav:
                    cur.execute(
                        "DELETE FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                        (fav_id, int(song_id)),
                    )
                else:
                    cur.execute(
                        "SELECT COALESCE(MAX(orden), 0) + 1 FROM playlist_canciones WHERE id_playlist = ?",
                        (fav_id,),
                    )
                    nxt = cur.fetchone()[0]
                    cur.execute(
                        "INSERT INTO playlist_canciones (id_playlist, id_cancion, orden) VALUES (?, ?, ?)",
                        (fav_id, int(song_id), nxt),
                    )
                conn.commit()
                return {"ok": True, "data": {"favorite": not is_fav}}
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def is_favorite(self, song_id: str) -> dict:
        try:
            fav_id = self._ensure_favorites_playlist()
            if not fav_id:
                return {"ok": True, "data": {"favorite": False}}
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT 1 FROM playlist_canciones WHERE id_playlist = ? AND id_cancion = ?",
                    (fav_id, int(song_id)),
                )
                is_fav = cur.fetchone() is not None
                return {"ok": True, "data": {"favorite": is_fav}}
            finally:
                conn.close()
        except Exception:
            return {"ok": True, "data": {"favorite": False}}
