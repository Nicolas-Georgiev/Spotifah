# conversor_controller.py
"""Consolidated controller for managing converters with a robust MVC pattern"""

import os
import sys
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


class BaseController(ABC):
    """Base controller defining the common interface for all converters"""
    
    def __init__(self):
        """Initialize controller"""
        self.model = None
        self.view = None
        self._setup_environment()
    
    def _setup_environment(self):
        """Set up the necessary environment (directories, etc.)"""
        self._ensure_data_directories()
    
    def _ensure_data_directories(self):
        """Create required directories if they don't exist"""
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        directories = [
            os.path.join(base_dir, "data", "music"),
            os.path.join(base_dir, "data", "metadata"),
            os.path.join(base_dir, "data", "temp")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @abstractmethod
    def validate_input(self, input_data: str) -> bool:
        """Validate user input"""
        pass
    
    @abstractmethod
    def process_conversion(self, input_data: str) -> str:
        """Process conversion using the model"""
        pass
    
    def handle_error(self, error: Exception) -> None:
        """Handle errors consistently"""
        error_msg = f"Error en conversión: {str(error)}"
        if self.view:
            self.view.show_error(error_msg)
        else:
            print(f"[ERR] {error_msg}")
    
    def handle_success(self, result: str) -> None:
        """Handle success consistently"""
        if self.view:
            self.view.show_result(result)
        else:
            print(f"[OK] Conversión completada: {result}")
    
    def show_progress(self, message: str) -> None:
        """Show progress to the user"""
        if self.view:
            self.view.show_message(message)
        else:
            print(f"[INFO] {message}")
    
    @abstractmethod
    def run(self) -> None:
        """Run the main controller flow"""
        pass


class ConversorController:
    """Main controller that manages multiple converters"""
    
    def __init__(self):
        """Initialize main controller"""
        from controller.spotify2mp3_controller import Spotify2MP3Controller
        from controller.youtube2mp3_controller import YouTube2MP3Controller
        from controller.soundcloud2mp3_controller import SoundCloud2MP3Controller
        
        self.controllers: Dict[str, BaseController] = {
            'spotify':    Spotify2MP3Controller(),
            'youtube':    YouTube2MP3Controller(),
            'soundcloud': SoundCloud2MP3Controller(),
        }
        self._setup_environment()
    
    def _setup_environment(self) -> None:
        """Set up general environment"""
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        directories = [
            os.path.join(base_dir, "data", "music"),
            os.path.join(base_dir, "data", "metadata"),
            os.path.join(base_dir, "data", "temp"),
            os.path.join(base_dir, "logs")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def show_main_menu(self) -> None:
        """Show main menu"""
        print("\n" + "="*70)
        print("  [MUSIC] EKHO - PLATAFORMA MUSICAL [MUSIC]")
        print("="*70)
        print("\n[LIST] CONVERTIDORES DISPONIBLES:")
        print("  1⃣  Spotify a MP3  (pistas, playlists y álbumes)")
        print("  2⃣  YouTube a MP3  (vídeos y playlists)")
        print("  3⃣  SoundCloud a MP3  (pistas y sets/playlists)")
        print("\n[CONFIG]  OTRAS OPCIONES:")
        print("  4⃣  Estado del sistema")
        print("  5⃣  Ver canciones en la base de datos")
        print("  0⃣  Salir")
        print("="*70)
    
    def get_user_choice(self) -> str:
        """Get user choice"""
        while True:
            try:
                print("\nSelecciona una opción (1-3, 0 para salir): ", end='', flush=True)
                choice = input().strip()
                
                if choice in ['1', '2', '3', '4', '5', '0']:
                    return choice
                else:
                    print("\u274c Opción no válida. Por favor selecciona 1, 2, 3, 4, 5 o 0.")
                    
            except EOFError:
                print("\n[ERR] EOF detectado - finalizando programa")
                return "0"
            except KeyboardInterrupt:
                print("\n[ERR] Operación cancelada por el usuario")
                return "0"
            except Exception as e:
                print(f"\n[ERR] Error inesperado: {e}")
                return "0"
    
    def show_system_status(self) -> None:
        """Show system status"""
        print("\n[TOOL] ESTADO DEL SISTEMA:")
        
        dependencies = [
            ('spotdl', 'SpotDL para metadatos de Spotify'),
            ('yt_dlp', 'yt-dlp para descargas de YouTube'),
            ('moviepy', 'MoviePy para conversión de audio'),
            ('mutagen', 'Mutagen para metadatos MP3'),
            ('requests', 'Requests para descargas HTTP'),
            ('pytubefix', 'PyTubefix para flujo de YouTube'),
            ('pkg_resources', 'setuptools/pkg_resources para compatibilidad spotdl')
        ]
        
        for dep, description in dependencies:
            try:
                __import__(dep)
                print(f"  [OK] {description}")
            except ImportError:
                print(f"  [ERR] {description} - NO INSTALADO")
        
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        directories = [
            ("data/music", "Directorio de música"),
            ("data/metadata", "Directorio de metadatos"),
            ("data/temp", "Directorio temporal")
        ]
        
        print("\n[FOLDER] DIRECTORIOS:")
        for dir_path, description in directories:
            full_path = os.path.join(base_dir, dir_path)
            if os.path.exists(full_path):
                print(f"  [OK] {description}: {full_path}")
            else:
                print(f"  [ERR] {description}: NO EXISTE")

        print("\n[CLIP] FFMPEG:")
        if self._is_ffmpeg_available():
            print("  [OK] FFmpeg disponible")
        else:
            print("  [ERR] FFmpeg no encontrado en PATH")
            print("  [TIP] Instalar en Windows: winget install Gyan.FFmpeg")

    @staticmethod
    def _is_ffmpeg_available() -> bool:
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def run(self) -> None:
        """Run the main flow"""
        try:
            while True:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice == '0':
                    print("\n[HELLO] ¡Gracias por usar Ekho! Hasta luego.")
                    break
                elif choice == '1':
                    print("\n[MUSIC] Iniciando conversor de Spotify...")
                    try:
                        self.controllers['spotify'].run()
                    except Exception as e:
                        print(f"[ERR] Error en conversor de Spotify: {e}")
                elif choice == '2':
                    print("\n[CAM] Iniciando conversor de YouTube...")
                    try:
                        self.controllers['youtube'].run()
                    except Exception as e:
                        print(f"[ERR] Error en conversor de YouTube: {e}")
                elif choice == '3':
                    print("\n[CLOUD] Iniciando conversor de SoundCloud...")
                    try:
                        self.controllers['soundcloud'].run()
                    except Exception as e:
                        print(f"[ERR] Error en conversor de SoundCloud: {e}")
                elif choice == '4':
                    self.show_system_status()
                elif choice == '5':
                    from run_conversores import show_songs
                    show_songs()
                
                print("\n[PAUSE]  Presiona Enter para continuar...", end='', flush=True)
                try:
                    input()
                except (EOFError, KeyboardInterrupt):
                    print()
                
        except KeyboardInterrupt:
            print("\n\n[STOP]  Programa terminado por el usuario. ¡Hasta luego!")
        except Exception as e:
            print(f"\n[ERR] Error crítico: {str(e)}")
