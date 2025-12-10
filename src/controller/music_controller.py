try:
    import pygame
    HAS_PYGAME = True
    print("✅ pygame disponible - Reproductor musical habilitado")
except ImportError:
    HAS_PYGAME = False
    print("⚠️ pygame no disponible - Reproductor musical deshabilitado")
    print("   Los conversores funcionarán normalmente")

class MusicController:
    def __init__(self, library):
        if HAS_PYGAME:
            pygame.mixer.init()
        else:
            print("⚠️ Reproductor musical no disponible (pygame no instalado)")
        self.library = library
        self.current_index = 0

    def play(self):
        if not HAS_PYGAME:
            print("❌ No se puede reproducir: pygame no está instalado")
            print("   Para habilitar el reproductor: pip install pygame")
            return
            
        track = self.library.get_track(self.current_index)
        if track:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            print(f"🎵 Reproduciendo: {track}")

    @staticmethod
    def pause():
        if not HAS_PYGAME:
            print("❌ No se puede pausar: pygame no está instalado")
            return
        pygame.mixer.music.pause()

    @staticmethod
    def resume():
        if not HAS_PYGAME:
            print("❌ No se puede reanudar: pygame no está instalado")
            return
        pygame.mixer.music.unpause()

    @staticmethod
    def stop():
        if not HAS_PYGAME:
            print("❌ No se puede detener: pygame no está instalado")
            return
        pygame.mixer.music.stop()

    def next_track(self):
        if not HAS_PYGAME:
            print("❌ No se puede cambiar pista: pygame no está instalado")
            return
        self.current_index = (self.current_index + 1) % self.library.total_tracks()
        self.play()

    def previous_track(self):
        if not HAS_PYGAME:
            print("❌ No se puede cambiar pista: pygame no está instalado")
            return
        self.current_index = (self.current_index - 1) % self.library.total_tracks()
        self.play()
