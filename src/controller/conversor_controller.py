# conversor_controller.py
"""Controlador consolidado para manejo de conversores con patrón MVC robusto"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict

# Configurar rutas de importación
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)


class BaseController(ABC):
    """Controlador base que define la interfaz común para todos los convertidores"""
    
    def __init__(self):
        """Inicializar controlador"""
        self.model = None
        self.view = None
        self._setup_environment()
    
    def _setup_environment(self):
        """Configurar el entorno necesario (carpetas, etc.)"""
        self._ensure_data_directories()
    
    def _ensure_data_directories(self):
        """Crear directorios necesarios si no existen"""
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
        """Validar entrada del usuario"""
        pass
    
    @abstractmethod
    def process_conversion(self, input_data: str) -> str:
        """Procesar conversión usando el modelo"""
        pass
    
    def handle_error(self, error: Exception) -> None:
        """Manejar errores de manera consistente"""
        error_msg = f"Error en conversión: {str(error)}"
        if self.view:
            self.view.show_error(error_msg)
        else:
            print(f"❌ {error_msg}")
    
    def handle_success(self, result: str) -> None:
        """Manejar éxito de manera consistente"""
        if self.view:
            self.view.show_result(result)
        else:
            print(f"✅ Conversión completada: {result}")
    
    def show_progress(self, message: str) -> None:
        """Mostrar progreso al usuario"""
        if self.view:
            self.view.show_message(message)
        else:
            print(f"ℹ️ {message}")
    
    @abstractmethod
    def run(self) -> None:
        """Ejecutar el flujo principal del controlador"""
        pass


class ConversorController:
    """Controlador principal que maneja múltiples convertidores"""
    
    def __init__(self):
        """Inicializar controlador principal"""
        # Importar controladores aquí para evitar importaciones circulares
        from controller.spotify2mp3_controller import Spotify2MP3Controller
        from controller.youtube2mp3_controller import YouTube2MP3Controller
        
        self.controllers: Dict[str, BaseController] = {
            'spotify': Spotify2MP3Controller(),
            'youtube': YouTube2MP3Controller()
        }
        self._setup_environment()
    
    def _setup_environment(self) -> None:
        """Configurar entorno general"""
        # Crear directorios base
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
        """Mostrar menú principal"""
        print("\n" + "="*70)
        print("  🎵 EKHO - PLATAFORMA MUSICAL 🎵")
        print("="*70)
        print("\n📋 CONVERTIDORES DISPONIBLES:")
        print("  1️⃣  Spotify a MP3")
        print("  2️⃣  YouTube a MP3")
        print("  0️⃣  Salir")
        print("="*70)
    
    def get_user_choice(self) -> str:
        """Obtener elección del usuario"""
        while True:
            try:
                print("\nSelecciona una opción (1-2, 0 para salir): ", end='', flush=True)
                choice = input().strip()
                
                if choice in ['1', '2', '0']:
                    return choice
                else:
                    print("❌ Opción no válida. Por favor selecciona 1, 2 o 0.")
                    
            except EOFError:
                print("\n❌ EOF detectado - finalizando programa")
                return "0"
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario")
                return "0"
            except Exception as e:
                print(f"\n❌ Error inesperado: {e}")
                return "0"
    
    def show_system_status(self) -> None:
        """Mostrar estado del sistema"""
        print("\n🔧 ESTADO DEL SISTEMA:")
        
        # Verificar dependencias
        dependencies = [
            ('spotdl', 'SpotDL para metadatos de Spotify'),
            ('yt_dlp', 'yt-dlp para descargas de YouTube'),
            ('moviepy', 'MoviePy para conversión de audio'),
            ('mutagen', 'Mutagen para metadatos MP3'),
            ('requests', 'Requests para descargas HTTP')
        ]
        
        for dep, description in dependencies:
            try:
                __import__(dep)
                print(f"  ✅ {description}")
            except ImportError:
                print(f"  ❌ {description} - NO INSTALADO")
        
        # Verificar directorios
        base_dir = os.path.join(os.path.dirname(__file__), "..", "..")
        directories = [
            ("data/music", "Directorio de música"),
            ("data/metadata", "Directorio de metadatos"),
            ("data/temp", "Directorio temporal")
        ]
        
        print("\n📁 DIRECTORIOS:")
        for dir_path, description in directories:
            full_path = os.path.join(base_dir, dir_path)
            if os.path.exists(full_path):
                print(f"  ✅ {description}: {full_path}")
            else:
                print(f"  ❌ {description}: NO EXISTE")
    
    def run(self) -> None:
        """Ejecutar el flujo principal"""
        try:
            while True:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice == '0':
                    print("\n👋 ¡Gracias por usar Ekho! Hasta luego.")
                    break
                elif choice == '1':
                    print("\n🎵 Iniciando conversor de Spotify...")
                    try:
                        self.controllers['spotify'].run()
                    except Exception as e:
                        print(f"❌ Error en conversor de Spotify: {e}")
                elif choice == '2':
                    print("\n🎥 Iniciando conversor de YouTube...")
                    try:
                        self.controllers['youtube'].run()
                    except Exception as e:
                        print(f"❌ Error en conversor de YouTube: {e}")
                
                # Pausa antes de volver al menú
                print("\n⏸️  Presiona Enter para continuar...", end='', flush=True)
                input()
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Programa terminado por el usuario. ¡Hasta luego!")
        except Exception as e:
            print(f"\n❌ Error crítico: {str(e)}")
