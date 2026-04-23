import os

class MusicLibrary:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.tracks = self._load_tracks()

    def _load_tracks(self):
        if not os.path.isdir(self.music_folder):
            os.makedirs(self.music_folder, exist_ok=True)
            return []

        tracks = [
            os.path.join(self.music_folder, f)
            for f in os.listdir(self.music_folder)
            if f.lower().endswith('.mp3')
        ]
        tracks.sort(key=lambda path: os.path.basename(path).lower())
        return tracks

    def reload_tracks(self):
        """Recarga la librería de pistas desde disco."""
        self.tracks = self._load_tracks()
        return self.tracks

    def get_track(self, index):
        if 0 <= index < len(self.tracks):
            return self.tracks[index]
        return None

    def total_tracks(self):
        return len(self.tracks)
