"""
frozen_utils.py
Utilidades de resolución de rutas para modo frozen (PyInstaller --onedir).

En modo desarrollo las rutas se calculan desde __file__.
En modo frozen (exe) PyInstaller aplana src/model/ → model/, src/databaseManager/ → databaseManager/,
por lo que las rutas relativas con múltiples ".." quedan incorrectas.
Este módulo centraliza la lógica para obtener siempre la ruta correcta.
"""

import os
import sys


def get_app_root() -> str:
    """
    Devuelve la raíz de la aplicación:
    - Frozen (exe): sys._MEIPASS  (= carpeta del exe con --onedir)
    - Desarrollo:   raíz del proyecto (padre de src/)
    """
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    # En desarrollo: este archivo está en src/, sube un nivel
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_data_dir() -> str:
    """
    Devuelve el directorio de datos del usuario:
    - Frozen: %AppData%/EKHO/data  (Windows)
    - Desarrollo: <project_root>/data
    """
    if getattr(sys, "frozen", False):
        if sys.platform == "win32":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif sys.platform == "darwin":
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        else:
            base = os.path.join(os.path.expanduser("~"), ".local", "share")
        return os.path.join(base, "EKHO", "data")
    return os.path.join(get_app_root(), "data")


def get_music_dir() -> str:
    return os.path.join(get_data_dir(), "music")


def get_db_path() -> str:
    return os.path.join(get_data_dir(), "BDD", "ekho.db")


def get_dotenv_path() -> str:
    return os.path.join(get_app_root(), ".env")
