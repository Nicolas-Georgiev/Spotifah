import os
import time
import importlib

try:
    pygame = importlib.import_module("pygame")
    HAS_PYGAME = True
    print("✅ pygame disponible - Reproductor musical habilitado")
except ImportError:
    HAS_PYGAME = False
    print("⚠️ pygame no disponible - Reproductor musical deshabilitado")
    print("   Los conversores funcionarán normalmente")

class MusicController:
    def __init__(self, library):
        self.library = library
        self.current_index = 0
        self.mixer_ready = False
        self._start_time = 0.0
        self._start_pos = 0.0
        self._paused_pos = 0.0
        self._is_paused = False

        self._queue_paths: list[str] = []
        self._queue_ids: list[int] = []
        self._queue_index: int = 0

        if HAS_PYGAME:
            try:
                pygame.mixer.init()
                self.mixer_ready = True
            except Exception as e:
                print(f"⚠️ No se pudo inicializar el reproductor: {e}")
                print("   Verifica dispositivo de audio disponible")
        else:
            print("⚠️ Reproductor musical no disponible (pygame no instalado)")

    def _can_control_playback(self):
        if not HAS_PYGAME:
            print("❌ Acción no disponible: pygame no está instalado")
            return False
        if not self.mixer_ready:
            print("❌ Acción no disponible: mezclador de audio no inicializado")
            return False
        return True

    def get_absolute_position(self) -> float:
        if self._is_paused:
            return self._paused_pos
        if self._start_time == 0:
            return 0.0
        return self._start_pos + (time.time() - self._start_time)

    def has_queue(self) -> bool:
        return len(self._queue_paths) > 0

    def set_queue(self, paths: list[str], ids: list[int], start_index: int = 0):
        self._queue_paths = paths
        self._queue_ids = ids
        self._queue_index = start_index

    def clear_queue(self):
        self._queue_paths = []
        self._queue_ids = []
        self._queue_index = 0

    def remove_from_queue(self, song_id: int) -> bool:
        if not self.has_queue():
            return False
        try:
            idx = self._queue_ids.index(song_id)
        except ValueError:
            return False
        self._queue_paths.pop(idx)
        self._queue_ids.pop(idx)
        if self._queue_index > idx:
            self._queue_index -= 1
        elif self._queue_index == idx:
            if len(self._queue_paths) > 0:
                self._queue_index = min(self._queue_index, len(self._queue_paths) - 1)
            else:
                self._queue_index = 0
        return True

    def _play_path(self, file_path: str):
        if not self._can_control_playback():
            return
        if not file_path or not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            return
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            self._start_time = time.time()
            self._start_pos = 0.0
            self._paused_pos = 0.0
            self._is_paused = False
            print(f"🎵 Reproduciendo: {file_path}")
        except Exception as e:
            print(f"❌ Error al reproducir archivo: {e}")

    def play_from_queue(self, queue_index: int = None) -> bool:
        if not self._can_control_playback():
            return False
        if not self.has_queue():
            print("⚠️ No hay cola de reproducción")
            return False
        if queue_index is not None:
            self._queue_index = queue_index
        if self._queue_index < 0 or self._queue_index >= len(self._queue_paths):
            self._queue_index = 0
        path = self._queue_paths[self._queue_index]
        if not path or not os.path.exists(path):
            print(f"❌ Archivo no encontrado en cola: {path}")
            return False
        self._play_path(path)
        return True

    def play(self) -> bool:
        if not self._can_control_playback():
            return False

        if self.has_queue():
            if self._queue_index >= len(self._queue_paths):
                self._queue_index = 0
            path = self._queue_paths[self._queue_index]
            if path and os.path.exists(path):
                self._play_path(path)
                return True
            print("❌ Archivo no encontrado en cola")
            return False

        if self.library.total_tracks() == 0:
            print("⚠️ No hay pistas MP3 en la biblioteca")
            return False

        if self.current_index >= self.library.total_tracks():
            self.current_index = 0

        track = self.library.get_track(self.current_index)
        if track and os.path.exists(track):
            self._play_path(track)
            return True
        else:
            print("❌ No se pudo reproducir: archivo no encontrado")
            return False

    def play_file(self, file_path):
        """
        Reproduce un archivo de audio específico.
        Si hay cola activa, busca y actualiza _queue_index.
        Si no hay cola, busca en library.tracks.
        Retorna True si se reprodujo correctamente, False en caso contrario.
        """
        if not self._can_control_playback():
            return False
        if not file_path:
            print("❌ Ruta de archivo vacía")
            return False
        abs_path = os.path.normpath(os.path.abspath(file_path))
        if not os.path.exists(abs_path):
            print(f"❌ Archivo no encontrado: {abs_path}")
            return False
        try:
            normalized = os.path.normpath(abs_path)

            if self.has_queue():
                found = False
                for i, p in enumerate(self._queue_paths):
                    if os.path.normpath(p) == normalized:
                        self._queue_index = i
                        found = True
                        break
                if not found:
                    self._queue_paths.append(normalized)
                    self._queue_ids.append(0)
                    self._queue_index = len(self._queue_paths) - 1
            else:
                self.current_index = 0
                for i, t in enumerate(self.library.tracks):
                    if os.path.normpath(t) == normalized:
                        self.current_index = i
                        break

            self._play_path(abs_path)
            return True
        except Exception as e:
            print(f"❌ Error al reproducir archivo: {e}")
            return False

    def pause(self):
        if not self._can_control_playback():
            return
        self._paused_pos = self._start_pos + (time.time() - self._start_time)
        self._is_paused = True
        pygame.mixer.music.pause()

    def resume(self):
        if not self._can_control_playback():
            return
        self._start_time = time.time()
        self._start_pos = self._paused_pos
        self._is_paused = False
        pygame.mixer.music.unpause()

    def stop(self):
        if not self._can_control_playback():
            return
        self._start_time = 0.0
        self._start_pos = 0.0
        self._paused_pos = 0.0
        self._is_paused = False
        pygame.mixer.music.stop()

    def seek(self, position_seconds):
        if not self._can_control_playback():
            return False
        if self.has_queue():
            if self._queue_index >= len(self._queue_paths):
                return False
            track = self._queue_paths[self._queue_index]
        else:
            track = self.library.get_track(self.current_index)
        if track and os.path.exists(track):
            try:
                pygame.mixer.music.load(track)
                pygame.mixer.music.play(start=position_seconds)
                self._start_time = time.time()
                self._start_pos = position_seconds
                self._paused_pos = 0.0
                self._is_paused = False
                return True
            except Exception as e:
                print(f"❌ Error al hacer seek: {e}")
                return False
        return False

    def next_track(self):
        if not self._can_control_playback():
            return
        if self.has_queue():
            if len(self._queue_paths) == 0:
                print("⚠️ No hay pistas en la cola")
                return
            self._queue_index = (self._queue_index + 1) % len(self._queue_paths)
            self._play_path(self._queue_paths[self._queue_index])
        else:
            if self.library.total_tracks() == 0:
                print("⚠️ No hay pistas MP3 en la biblioteca")
                return
            self.current_index = (self.current_index + 1) % self.library.total_tracks()
            self.play()

    def previous_track(self):
        if not self._can_control_playback():
            return
        if self.has_queue():
            if len(self._queue_paths) == 0:
                print("⚠️ No hay pistas en la cola")
                return
            self._queue_index = (self._queue_index - 1) % len(self._queue_paths)
            self._play_path(self._queue_paths[self._queue_index])
        else:
            if self.library.total_tracks() == 0:
                print("⚠️ No hay pistas MP3 en la biblioteca")
                return
            self.current_index = (self.current_index - 1) % self.library.total_tracks()
            self.play()
