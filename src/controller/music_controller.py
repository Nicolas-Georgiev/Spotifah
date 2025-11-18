import pygame

class MusicController:
    def __init__(self, library):
        pygame.mixer.init()
        self.library = library
        self.current_index = 0

    def play(self):
        track = self.library.get_track(self.current_index)
        if track:
            pygame.mixer.music.load(track)
            pygame.mixer.music.play()
            print(f"🎵 Reproduciendo: {track}")

    @staticmethod
    def pause():
        pygame.mixer.music.pause()

    @staticmethod
    def resume():
        pygame.mixer.music.unpause()

    @staticmethod
    def stop():
        pygame.mixer.music.stop()

    def next_track(self):
        self.current_index = (self.current_index + 1) % self.library.total_tracks()
        self.play()

    def previous_track(self):
        self.current_index = (self.current_index - 1) % self.library.total_tracks()
        self.play()
