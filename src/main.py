import os
from model.music_library import MusicLibrary
from controller.music_controller import MusicController
from view.player_ui import PlayerUI

def main():
    music_path = os.path.join("data", "music")
    library = MusicLibrary(music_path)
    controller = MusicController(library)
    ui = PlayerUI(controller)
    ui.run()

if __name__ == "__main__":
    main()
