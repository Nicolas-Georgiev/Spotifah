# conversor_view.py
"""Vista base para implementar patrón MVC robusto"""

from abc import ABC, abstractmethod
from typing import List, Optional
import sys
import os


class BaseView(ABC):
    """Vista base que define la interfaz común para todas las vistas"""
    
    def __init__(self):
        """Inicializar vista"""
        self.app_name = "Ekho Converter"
        self.version = "v2.0"
    
    def show_welcome(self) -> None:
        """Mostrar mensaje de bienvenida genérico"""
        print("\n" + "="*60)
        print(f"  🎵 {self.get_converter_name()} 🎵")
        print(f"  {self.get_converter_description()}")
        print(f"  {self.app_name} {self.version}")
        print("="*60 + "\n")
    
    @abstractmethod
    def get_converter_name(self) -> str:
        """Obtener nombre del convertidor"""
        pass
    
    @abstractmethod
    def get_converter_description(self) -> str:
        """Obtener descripción del convertidor"""
        pass
    
    @abstractmethod
    def get_user_input(self) -> str:
        """Obtener entrada del usuario"""
        pass
    
    def get_user_input_safe(self, prompt: str) -> str:
        """Obtener entrada del usuario con manejo mejorado para PowerShell"""
        try:
            print(prompt, end='', flush=True)
            user_input = input().strip()
            return user_input
        except (EOFError, KeyboardInterrupt):
            print("\n\n❌ Operación cancelada por el usuario.")
            return ""
        except Exception as e:
            print(f"\n❌ Error al leer entrada: {e}")
            return ""
    
    @abstractmethod
    def show_supported_formats(self) -> None:
        """Mostrar formatos soportados"""
        pass
    
    def show_message(self, message: str) -> None:
        """Mostrar mensaje informativo"""
        print(f"ℹ️  {message}")
    
    def show_success(self, message: str) -> None:
        """Mostrar mensaje de éxito"""
        print(f"\n✅ {message}")
    
    def show_error(self, error_message: str) -> None:
        """Mostrar mensaje de error"""
        print(f"\n❌ Error: {error_message}\n")
    
    def show_result(self, file_path: str) -> None:
        """Mostrar resultado de conversión"""
        print(f"\n🎉 ¡Conversión completada!")
        print(f"📁 Archivo guardado en: {file_path}")
        print(f"🎜️ El archivo incluye metadatos y portada\n")
    
    def show_progress_steps(self, steps: List[str]) -> None:
        """Mostrar pasos del proceso"""
        print("\n📋 Proceso de conversión:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
        print()
    
    def ask_continue(self) -> bool:
        """Preguntar si continuar"""
        response = input("¿Deseas convertir otra pista? (s/n): ").lower().strip()
        return response in ['s', 'si', 'sí', 'y', 'yes']
    
    def show_goodbye(self) -> None:
        """Mostrar mensaje de despedida"""
        print("\n" + "="*50)
        print(f"  ¡Gracias por usar {self.app_name}!")
        print("="*50 + "\n")
    
    def show_instructions(self, instructions: List[str]) -> None:
        """Mostrar instrucciones detalladas"""
        print("\n" + "="*70)
        print("  📋 INSTRUCCIONES DE USO")
        print("="*70)
        
        for i, instruction in enumerate(instructions, 1):
            print(f"\n{i}. {instruction}")
        
        print("\n" + "="*70 + "\n")
