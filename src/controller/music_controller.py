import pygame
import random


class MusicController:


    def __init__(self, library):
        pygame.mixer.init()
        self.library = library
        self.current_index = 0
        self.random_mode = False  # 🔁 Modo aleatorio desactivado por defecto
        self.volume = 1 
        pygame.mixer.music.set_volume(self.volume)


    def play(self):
        track = self.library.get_track(self.current_index)
        if track:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            print(f"🎵 Reproduciendo: {track}")
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
    def play_random(self):
        if self.library.total_tracks() > 0:
            self.current_index = random.randint(0, self.library.total_tracks() - 1)
            self.play()

    def pause(self):
        pygame.mixer.music.pause()

    def resume(self):
        pygame.mixer.music.unpause()

    def stop(self):
        pygame.mixer.music.stop()

    def next_track(self):
        if self.random_mode:
            self.play_random()
        else:
            self.current_index = (self.current_index + 1) % self.library.total_tracks()
            self.play()

    def previous_track(self):
        self.current_index = (self.current_index - 1) % self.library.total_tracks()
        self.play()
    def loop_track(self):
        track = self.library.get_track(self.current_index)
        if track:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play(loops=-1)  # -1 significa bucle infinito
            print(f"🔁 Reproduciendo en bucle: {track}")
    def toggle_random_mode(self):
        self.random_mode = not self.random_mode
        state = "activado" if self.random_mode else "desactivado"
        print(f"🔀 Modo aleatorio {state}")
    def set_volume(self, percent):
        try:
            value = max(0, min(int(percent), 100)) / 100.0
            self.volume = value
            pygame.mixer.music.set_volume(self.volume)
            print(f"🎚️ Volumen ajustado a {int(self.volume * 100)}%")
        except ValueError:
            print("❌ Usa un número válido entre 0 y 100.")