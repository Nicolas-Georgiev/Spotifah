# soundcloud2mp3_controller.py
"""Controller for SoundCloud to MP3 conversion following a robust MVC pattern"""

import os
import sys

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from controller.conversor_controller import BaseController
from model.soundcloud2mp3 import SoundCloudConverter


class SoundCloudView:
    """Minimal view for SoundCloud (same interface as other views)"""

    def get_user_input(self) -> str:
        print("\n🎵 Ingresa la URL de SoundCloud (pista o set/playlist):")
        print("  • https://soundcloud.com/artista/cancion")
        print("  • https://soundcloud.com/artista/sets/nombre-playlist\n")
        try:
            return input("URL: ").strip()
        except (EOFError, KeyboardInterrupt):
            return ""

    def show_welcome(self) -> None:
        print("\n" + "=" * 60)
        print("  🎵 CONVERSOR DE SOUNDCLOUD A MP3")
        print("=" * 60)

    def show_system_info(self) -> None:
        print("💡 Soporta pistas individuales y sets/playlists completas")

    def show_conversion_steps(self) -> None:
        print("\n📋 Pasos del proceso:")
        for s in [
            "🔍 Obtener información de la pista",
            "⬇️  Descargar audio",
            "🏷️  Añadir metadatos",
            "💾 Guardar archivo final",
        ]:
            print(f"  {s}")

    def show_result(self, result: str) -> None:
        print(f"\n✅ Descargado: {result}")

    def show_error(self, msg: str) -> None:
        print(f"\n❌ {msg}")

    def show_message(self, msg: str) -> None:
        print(f"ℹ️  {msg}")

    def ask_continue(self) -> bool:
        try:
            resp = input("\n¿Convertir otra URL? [s/N]: ").strip().lower()
            return resp in ("s", "si", "yes", "y")
        except (EOFError, KeyboardInterrupt):
            return False

    def show_goodbye(self) -> None:
        print("\n👋 Hasta luego desde SoundCloud.\n")


class SoundCloud2MP3Controller(BaseController):
    """Controller for SoundCloud to MP3 conversion"""

    def __init__(self):
        super().__init__()
        self.model = SoundCloudConverter()
        self.view = SoundCloudView()

    def validate_input(self, url: str) -> bool:  
        if not url or not url.strip():
            return False
        return "soundcloud.com" in url.strip()

    def process_conversion(self, url: str) -> str:  
        self.view.show_conversion_steps()
        self.show_progress("⬇️  Descargando desde SoundCloud...")
        return self.model.convert(url)

    def convert_single_track(self) -> bool:
        """Convert a single track or set/playlist - returns True on success"""
        try:
            url = self.view.get_user_input()

            if not self.validate_input(url):
                self.handle_error(ValueError(
                    "URL no válida. Debe ser un enlace de SoundCloud "
                    "(soundcloud.com/artista/cancion o /sets/...)"
                ))
                return False

            if self.model.is_playlist_url(url):
                print("\n📋 Set/playlist de SoundCloud detectado.")
                print("Obteniendo lista de pistas... (puede tardar unos segundos)")
                try:
                    track_urls = self.model.get_playlist_track_urls(url)
                    total = len(track_urls)
                except Exception as e:
                    self.handle_error(e)
                    return False

                print(f"\n🎵 Se encontraron {total} pistas.")
                confirm = input("¿Descargar todas? [s/N]: ").strip().lower()
                if confirm not in ("s", "si", "yes", "y"):
                    print("⏹️  Descarga cancelada.")
                    return False

                results = self.model.convert_playlist(url)
                print(f"\n✅ Descargadas {len(results)}/{total} pistas")
                return len(results) > 0

            result_path = self.process_conversion(url)
            self.handle_success(result_path)
            return True

        except KeyboardInterrupt:
            self.show_progress("⏹️  Operación cancelada por el usuario")
            return False
        except Exception as e:
            self.handle_error(e)
            return False

    def run(self) -> None:
        """Run the main controller flow"""
        try:
            self.view.show_welcome()
            self.view.show_system_info()

            while True:
                try:
                    self.convert_single_track()
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
