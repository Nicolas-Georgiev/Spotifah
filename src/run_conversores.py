#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EKHO - Plataforma Musical 

Punto de entrada principal que utiliza el patrón MVC mejorado con:
- Controladores como comunicadores entre Model y View
- Separación clara de responsabilidades
- Bibliotecas esenciales sin redundancias
"""

import os
import sys

# Obtener el directorio actual (src) y añadirlo al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def mostrar_canciones():
    """Muestra todas las canciones guardadas actualmente en la base de datos."""
    try:
        from model.db_adapter import _get_db
        db = _get_db()
        conn = db.get_connection()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT c.id_cancion, c.titulo, c.artista, c.album,
                       c.duracion_seg, c.plataforma_origen, c.ruta_local
                FROM canciones c
                ORDER BY c.id_cancion
            """)
            rows = cur.fetchall()
            if not rows:
                print("\n📭 No hay canciones en la base de datos.")
                return
            print(f"\n🎵 Canciones en la base de datos ({len(rows)} total):")
            print("-" * 70)
            for r in rows:
                duracion = f"{r['duracion_seg']}s" if r['duracion_seg'] else "-"
                ruta = r['ruta_local'] if r['ruta_local'] else "-"
                print(f"[{r['id_cancion']:>3}] {r['titulo']} — {r['artista']}")
                print(f"       Album: {r['album'] or '-'}  |  Duración: {duracion}  |  Origen: {r['plataforma_origen'] or '-'}")
                print(f"       Ruta: {ruta}")
                print()
        finally:
            conn.close()
    except Exception as e:
        print(f"\n❌ Error al consultar la BD: {e}")


def main():
    """Función principal que ejecuta la aplicación"""
    print(f"\n🎵 Iniciando Ekho Music Converter...")
    print(f"\n⚙️  Configurando terminal...")

    try:
        # Importar el controlador principal consolidado
        from controller.conversor_controller import ConversorController
        
        # Crear y ejecutar controlador principal consolidado
        conversor_controller = ConversorController()
        conversor_controller.run()
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("\n🔧 SOLUCIONES POSIBLES:")
        print("1. Verificar que todas las dependencias estén instaladas:")
        print("   python install_dependencies.py")
        print("\n2. Verificar que FFmpeg esté instalado:")
        print("   Windows: winget install Gyan.FFmpeg")
        print("   Linux: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario. ¡Hasta luego!")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("\n🔍 INFORMACIÓN DE DEBUG:")
        import traceback
        traceback.print_exc()
        
        print("\n💡 CONSEJOS PARA SOLUCIONAR:")
        print("1. Verificar que todas las dependencias estén correctamente instaladas")
        print("2. Ejecutar el instalador de dependencias: python install_dependencies.py")
        print("3. Verificar que FFmpeg esté disponible en el PATH del sistema")


if __name__ == "__main__":
    main()
