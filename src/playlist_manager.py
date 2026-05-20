"""
Archivo principal para ejecutar el gestor de playlists
Punto de entrada del sistema de gestión de playlists
"""
import sys
import os

# Añadir el directorio src al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.databaseManager.db import Database
from src.model.playlist_model import PlaylistModel
from src.controller.playlist_controller import PlaylistController
from src.view.playlist_view import PlaylistView


def main():
    """
    Función principal que inicializa y ejecuta el gestor de playlists
    """
    print("🎵 Iniciando Gestor de Playlists...")
    
    # Inicializar la base de datos
    db = Database()
    print("✅ Base de datos conectada")
    
    # Inicializar el modelo
    model = PlaylistModel(db)
    print("✅ Modelo inicializado")
    
    # Inicializar el controlador
    controller = PlaylistController(model)
    print("✅ Controlador inicializado")
    
    # Establecer usuario por defecto (puedes cambiarlo según tu sistema de login)
    # Por defecto usa el usuario con ID 1 (Juan, según la BD de ejemplo)
    controller.set_current_user(1)
    print(f"✅ Usuario establecido: ID {controller.current_user_id}")
    
    # Inicializar la vista
    view = PlaylistView(controller)
    print("✅ Vista inicializada")
    
    print("\n" + "="*60)
    print("Todo listo! Iniciando interfaz...")
    print("="*60)
    
    input("\n[Presiona Enter para continuar...]")
    
    # Ejecutar la interfaz
    view.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa terminado por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
