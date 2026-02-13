#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EKHO - Conversor Universal
Punto de acceso principal desde la raíz del proyecto

Este archivo llama al conversor principal ubicado en src/run_conversores.py
"""

import os
import sys

def main():
    """Función principal que ejecuta el conversor desde la raíz"""
    try:
        # Obtener la ruta al archivo run_conversores.py en la carpeta src
        current_dir = os.path.dirname(os.path.abspath(__file__))
        run_conversores_path = os.path.join(current_dir, "src", "run_conversores.py")
        
        # Verificar que el archivo existe
        if not os.path.exists(run_conversores_path):
            print("❌ Error: No se encontró el archivo src/run_conversores.py")
            print(f"   Ruta buscada: {run_conversores_path}")
            return False
        
        # Añadir src al path y ejecutar run_conversores
        src_dir = os.path.join(current_dir, "src")
        sys.path.insert(0, src_dir)
        
        # Importar y ejecutar el módulo principal
        import run_conversores
        run_conversores.main()  # Llamar explícitamente a la función main()
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("\n🔧 SOLUCIONES:")
        print("1. Verificar que src/run_conversores.py existe")
        print("2. Instalar dependencias: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    main()