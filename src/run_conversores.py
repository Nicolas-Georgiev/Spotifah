#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EKHO - Plataforma Musical

Entry point using the improved MVC pattern with:
- Controllers as communicators between Model and View
- Clear separation of responsibilities
- Essential libraries without redundancies
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def show_songs():
    """Show all songs currently stored in the database."""
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
                duration = f"{r['duracion_seg']}s" if r['duracion_seg'] else "-"
                path = r['ruta_local'] if r['ruta_local'] else "-"
                print(f"[{r['id_cancion']:>3}] {r['titulo']} — {r['artista']}")
                print(f"       Album: {r['album'] or '-'}  |  Duración: {duration}  |  Origen: {r['plataforma_origen'] or '-'}")
                print(f"       Ruta: {path}")
                print()
        finally:
            conn.close()
    except Exception as e:
        print(f"\n❌ Error al consultar la BD: {e}")


def main():
    """Main function that runs the application"""
    print(f"\n🎵 Iniciando Ekho Music Converter...")
    print(f"\n⚙️  Configurando terminal...")

    try:
        from controller.conversor_controller import ConversorController
        
        conversor_controller = ConversorController()
        conversor_controller.run()
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("\n🔧 SOLUCIONES POSIBLES:")
        print("1. Verificar que todas las dependencias estén instaladas:")
        print("   python scripts\install_dependencies.py")
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
        print("2. Ejecutar el instalador de dependencias: python scripts\install_dependencies.py")
        print("3. Verificar que FFmpeg esté disponible en el PATH del sistema")


if __name__ == "__main__":
    main()
