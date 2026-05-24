# spotify2mp3_controller.py
"""Controller for Spotify to MP3 conversion following a robust MVC pattern"""

import os
import sys
from typing import Optional

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from controller.conversor_controller import BaseController
from model.spotify2mp3_model import Spotify2MP3Converter
from view.spotify2mp3_view import SpotifyView


class Spotify2MP3Controller(BaseController):
    """Controller for Spotify to MP3 conversion"""
    
    def __init__(self):
        """Initialize Spotify controller"""
        super().__init__()
        self.model = Spotify2MP3Converter()
        self.view = SpotifyView()
        self.current_session = None
    
    def validate_input(self, url: str) -> bool: # type: ignore
        """Validate that the URL is from Spotify"""
        if not url or not url.strip():
            return False
        
        url = url.strip()
        spotify_indicators = [
            "spotify.com",
            "spotify:",
            "open.spotify.com"
        ]
        
        return any(indicator in url for indicator in spotify_indicators)
    
    def process_conversion(self, spotify_url: str) -> str: # type: ignore
        """Process Spotify to MP3 conversion"""
        self.view.show_conversion_steps()
        self.show_progress("🔍 Extrayendo metadatos de Spotify...")
        return self.model.convert(spotify_url)
    
    def convert_single_track(self) -> bool:
        """Convert a single track or full playlist - returns True on success"""
        try:
            url = self.view.get_user_input()

            if not self.validate_input(url):
                self.handle_error(ValueError(
                    "URL no válida. Debe ser un enlace de Spotify válido "
                    "(open.spotify.com/track|playlist|album/...)"
                ))
                return False

            if self.model.is_playlist_url(url):
                print("\n📋 Playlist/álbum de Spotify detectado.")
                print("Obteniendo lista de canciones... (puede tardar unos segundos)")
                try:
                    songs = self.model.get_playlist_songs(url)
                    total = len(songs)
                except Exception as e:
                    self.handle_error(e)
                    return False

                print(f"\n🎵 Se encontraron {total} canciones.")
                confirm = input("\u00bfDescargar todas? [s/N]: ").strip().lower()
                if confirm not in ('s', 'si', 'yes', 'y'):
                    print("⏹️  Descarga cancelada.")
                    return False

                results = self.model.convert_playlist(url)
                print(f"\n✅ Descargadas {len(results)}/{total} canciones")
                return len(results) > 0

            result_path = self.process_conversion(url)
            self.handle_success(result_path)
            self.view.show_metadata_info()
            return True

        except KeyboardInterrupt:
            self.show_progress("⏹️  Operación cancelada por el usuario")
            return False
        except Exception as e:
            self.handle_error(e)
            return False
    
    def show_setup_info(self) -> None:
        """Show setup information"""
        self.view.show_setup_info()
    
    def run(self) -> None:
        """Run the main controller flow"""
        try:
            self.view.show_welcome()
            self.view.show_system_info()
            
            while True:
                try:
                    success = self.convert_single_track()
                    
                    if not self.view.ask_continue():
                        break
                        
                except KeyboardInterrupt:
                    print("\n⏹️  Programa interrumpido por el usuario")
                    break
                except Exception as e:
                    self.handle_error(e)
                    if not self.view.ask_continue():
                        break
            
            self.view.show_goodbye()
            
        except KeyboardInterrupt:
            print("\n⏹️  Programa terminado")
        except Exception as e:
            self.handle_error(e)
