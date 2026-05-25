import os
import sys
import threading

_src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

import contextlib
import io
with contextlib.redirect_stdout(io.StringIO()):
    import pygame
    from model.music_library import MusicLibrary
    from controller.music_controller import MusicController, HAS_PYGAME

from api.covers import CoversMixin


class PlayerMixin(CoversMixin):
    def _init_player(self):
        if not self._pygame_inited:
            pygame.mixer.init()
            self.library = MusicLibrary(self._music_dir)
            self._music_controller = MusicController(self.library)
            settings = self.get_settings()
            saved_volume = settings.get("volume", 100)
            pygame.mixer.music.set_volume(saved_volume / 100.0)
            self._pygame_inited = True

    def _build_now_playing_dict(self):
        self._last_build_error = None
        try:
            if not self._pygame_inited:
                self._last_build_error = "pygame no inicializado"
                return None
            if not self._music_controller:
                self._last_build_error = "music_controller es None"
                return None
            if self._current_song_id is None:
                self._last_build_error = "_current_song_id es None"
                return None
            is_playing = bool(pygame.mixer.music.get_busy())
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id_cancion, titulo, artista, album, duracion_seg,
                           genero, plataforma_origen, ruta_local, caratula_url
                    FROM canciones WHERE id_cancion = ?
                """, (int(self._current_song_id),))
                row = cur.fetchone()
                if not row:
                    self._last_build_error = f"cancion {self._current_song_id} no encontrada en DB"
                    return None
                pos = self._music_controller.get_absolute_position()
                cover = row["caratula_url"] or ""
                if not cover:
                    cover = self._ensure_cover(row["id_cancion"], row["titulo"], row["artista"] or "", row["album"] or "", row["ruta_local"] or "", row["plataforma_origen"] or "")
                cover = self._localize_cover(row["id_cancion"], cover)
                return {
                    "id": str(row["id_cancion"]),
                    "title": row["titulo"],
                    "artist": row["artista"] or "",
                    "album": row["album"] or "",
                    "duration": row["duracion_seg"] or 0,
                    "cover_url": cover,
                    "is_playing": bool(is_playing),
                    "position": pos,
                    "shuffle": self._music_controller.get_shuffle_enabled(),
                    "repeat": self._music_controller.get_repeat_mode(),
                }
            finally:
                conn.close()
        except Exception as e:
            self._last_build_error = f"exception: {e}"
            return None

    def play_song(self, song_id: str, song_ids: list = None) -> dict:
        try:
            self._init_player()
            self.library.reload_tracks()
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT ruta_local, titulo FROM canciones WHERE id_cancion = ?",
                    (int(song_id),),
                )
                row = cur.fetchone()
                if not row or not row["ruta_local"]:
                    return {"ok": False, "error": "Cancion no encontrada en disco"}
                song_path = row["ruta_local"]
                if not os.path.exists(song_path):
                    filename = os.path.basename(song_path)
                    alt_path = os.path.join(self._music_dir, filename)
                    if os.path.exists(alt_path):
                        song_path = os.path.normpath(alt_path)
                        cur.execute(
                            "UPDATE canciones SET ruta_local = ? WHERE id_cancion = ?",
                            (song_path, int(song_id)),
                        )

                self._current_song_id = song_id

                if song_ids and len(song_ids) > 0:
                    queue_paths = []
                    queue_ids = []
                    start_index = 0
                    for sid in song_ids:
                        sid_int = int(sid)
                        cur.execute(
                            "SELECT ruta_local FROM canciones WHERE id_cancion = ?",
                            (sid_int,),
                        )
                        row2 = cur.fetchone()
                        if row2 and row2["ruta_local"]:
                            p = row2["ruta_local"]
                            if not os.path.exists(p):
                                fn = os.path.basename(p)
                                alt = os.path.join(self._music_dir, fn)
                                if os.path.exists(alt):
                                    p = os.path.normpath(alt)
                            p = os.path.normpath(os.path.abspath(p))
                            queue_paths.append(p)
                            queue_ids.append(sid_int)
                            if sid == song_id:
                                start_index = len(queue_paths) - 1
                    with self._player_lock:
                        self._music_controller.set_queue(
                            queue_paths, queue_ids, start_index
                        )
                        ok = self._music_controller.play_from_queue()
                        if not ok:
                            return {"ok": False, "error": "No se pudo reproducir desde la cola"}
                else:
                    with self._player_lock:
                        ok = self._music_controller.play_file(song_path)
                    if not ok:
                        return {"ok": False, "error": f"No se pudo reproducir: {song_path}"}
                cur.execute(
                    "INSERT INTO historial_reproduccion (id_usuario, id_cancion) VALUES (?, ?)",
                    (1, int(song_id)),
                )
                conn.commit()
                np_data = self._build_now_playing_dict()
                return {
                    "ok": True,
                    "data": {
                        "message": f"Reproduciendo: {os.path.basename(song_path)}",
                        "now_playing": np_data,
                    },
                }
            finally:
                conn.close()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def pause_song(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": False, "error": "Reproductor no inicializado"}
            with self._player_lock:
                self._music_controller.pause()
            return {"ok": True, "data": {"message": "Pausado"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def resume_song(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": False, "error": "Reproductor no inicializado"}
            with self._player_lock:
                self._music_controller.resume()
            return {"ok": True, "data": {"message": "Reanudado"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop_song(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": False, "error": "Reproductor no inicializado"}
            with self._player_lock:
                self._music_controller.stop()
            return {"ok": True, "data": {"message": "Detenido"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def seek_song(self, position: float) -> dict:
        try:
            if not self._pygame_inited or self._current_song_id is None:
                return {"ok": False, "error": "No hay canción reproduciendo"}
            with self._player_lock:
                ok = self._music_controller.seek(max(0, position))
            if not ok:
                return {"ok": False, "error": "No se pudo cambiar la posición"}
            return {"ok": True, "data": {"message": "Posición cambiada"}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _sync_current_song_from_player(self):
        try:
            if self._music_controller.has_queue():
                idx = self._music_controller._queue_index
                ids = self._music_controller._queue_ids
                if 0 <= idx < len(ids):
                    song_id = ids[idx]
                    self._current_song_id = str(song_id)
                    conn = self.db.get_connection()
                    try:
                        cur = conn.cursor()
                        cur.execute(
                            "INSERT INTO historial_reproduccion (id_usuario, id_cancion) VALUES (?, ?)",
                            (1, song_id),
                        )
                        conn.commit()
                    finally:
                        conn.close()
                    return
            idx = self._music_controller.current_index
            if 0 <= idx < len(self.library.tracks):
                track_path = os.path.normpath(self.library.tracks[idx])
                conn = self.db.get_connection()
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT id_cancion FROM canciones WHERE ruta_local = ?",
                        (track_path,),
                    )
                    row = cur.fetchone()
                    if row:
                        self._current_song_id = str(row["id_cancion"])
                        cur.execute(
                            "INSERT INTO historial_reproduccion (id_usuario, id_cancion) VALUES (?, ?)",
                            (1, row["id_cancion"]),
                        )
                        conn.commit()
                finally:
                    conn.close()
        except Exception as e:
            print(f"[sync_current_song] error: {e}")

    def next_song(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                self._music_controller.next_track()
                cid = self._music_controller.get_current_queue_id()
                if cid is not None:
                    self._current_song_id = str(cid)
            self._sync_current_song_from_player()
            np_data = self._build_now_playing_dict()
            return {
                "ok": True,
                "data": {
                    "message": "Siguiente cancion",
                    "now_playing": np_data,
                    "debug": {"last_build_error": self._last_build_error} if np_data is None else None,
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def prev_song(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                self._music_controller.previous_track()
                cid = self._music_controller.get_current_queue_id()
                if cid is not None:
                    self._current_song_id = str(cid)
            self._sync_current_song_from_player()
            np_data = self._build_now_playing_dict()
            return {
                "ok": True,
                "data": {
                    "message": "Cancion anterior",
                    "now_playing": np_data,
                    "debug": {"last_build_error": self._last_build_error} if np_data is None else None,
                },
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def toggle_shuffle(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                enabled = self._music_controller.toggle_shuffle()
            return {"ok": True, "data": {"shuffle": enabled}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def cycle_repeat(self) -> dict:
        try:
            self._init_player()
            with self._player_lock:
                mode = self._music_controller.cycle_repeat_mode()
            return {"ok": True, "data": {"repeat": mode}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_now_playing(self) -> dict:
        try:
            np_data = self._build_now_playing_dict()
            if np_data is None:
                debug = {
                    "pygame_inited": self._pygame_inited,
                    "music_controller": self._music_controller is not None,
                    "current_song_id": self._current_song_id,
                    "has_queue": self._music_controller.has_queue() if self._music_controller else None,
                    "queue_index": self._music_controller._queue_index if self._music_controller and self._music_controller.has_queue() else None,
                    "queue_ids_len": len(self._music_controller._queue_ids) if self._music_controller else None,
                    "mixer_ready": self._music_controller.mixer_ready if self._music_controller else None,
                    "HAS_PYGAME": HAS_PYGAME,
                    "last_build_error": getattr(self, "_last_build_error", None),
                }
                return {"ok": True, "data": None, "debug": debug}
            return {"ok": True, "data": np_data}
        except Exception as e:
            return {"ok": True, "data": None, "debug": {"error": str(e)}}

    def get_playback_position(self) -> dict:
        try:
            if not self._pygame_inited:
                return {"ok": True, "data": {"position": 0.0, "is_playing": False}}
            with self._player_lock:
                pos = self._music_controller.get_absolute_position()
                busy = bool(pygame.mixer.music.get_busy())
                return {"ok": True, "data": {"position": max(0.0, pos), "is_playing": busy}}
        except Exception:
            return {"ok": True, "data": {"position": 0.0, "is_playing": False}}

    def set_volume(self, volume: int) -> dict:
        try:
            v = max(0, min(100, int(volume)))
            if self._pygame_inited:
                pygame.mixer.music.set_volume(v / 100.0)
            settings = self.get_settings()
            settings["volume"] = v
            self.update_settings({"volume": v})
            return {"ok": True, "data": {"volume": v}}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_volume(self) -> dict:
        try:
            settings = self.get_settings()
            return {"ok": True, "data": {"volume": settings.get("volume", 100)}}
        except Exception:
            return {"ok": True, "data": {"volume": 100}}

    def get_recently_played(self, limit: int = 10) -> list:
        try:
            conn = self.db.get_connection()
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT c.id_cancion, c.titulo, c.artista, c.album, c.duracion_seg,
                              c.genero, c.plataforma_origen, c.ruta_local, c.caratula_url
                    FROM historial_reproduccion h
                    JOIN canciones c ON h.id_cancion = c.id_cancion
                    WHERE h.id_usuario = 1
                    GROUP BY c.id_cancion
                    ORDER BY MAX(h.fecha_reproduccion) DESC
                    LIMIT ?
                """, (limit,))
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
