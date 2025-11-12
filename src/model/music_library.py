import os

class MusicLibrary:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.tracks = self._load_tracks()

    def _load_tracks(self):
        return [
            os.path.join(self.music_folder, f)
            for f in os.listdir(self.music_folder)
            if f.endswith('.mp3')
        ]

    def get_track(self, index):
        if 0 <= index < len(self.tracks):
            return self.tracks[index]
        return None

    def total_tracks(self):
        return len(self.tracks)
