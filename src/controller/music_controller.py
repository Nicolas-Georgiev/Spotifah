import os
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

    def play(self):
        if not self._can_control_playback():
            return

        if self.library.total_tracks() == 0:
            print("⚠️ No hay pistas MP3 en la biblioteca")
            return

        if self.current_index >= self.library.total_tracks():
            self.current_index = 0
            
        track = self.library.get_track(self.current_index)
        if track and os.path.exists(track):
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            print(f"🎵 Reproduciendo: {track}")
        else:
            print("❌ No se pudo reproducir: archivo no encontrado")

    def pause(self):
        if not self._can_control_playback():
            return
        pygame.mixer.music.pause()

    def resume(self):
        if not self._can_control_playback():
            return
        pygame.mixer.music.unpause()

    def stop(self):
        if not self._can_control_playback():
            return
        pygame.mixer.music.stop()

    def next_track(self):
        if not self._can_control_playback():
            return
        if self.library.total_tracks() == 0:
            print("⚠️ No hay pistas MP3 en la biblioteca")
            return
        self.current_index = (self.current_index + 1) % self.library.total_tracks()
        self.play()

    def previous_track(self):
        if not self._can_control_playback():
            return
        if self.library.total_tracks() == 0:
            print("⚠️ No hay pistas MP3 en la biblioteca")
            return
        self.current_index = (self.current_index - 1) % self.library.total_tracks()
        self.play()
