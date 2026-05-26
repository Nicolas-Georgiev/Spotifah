#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para eliminar la carpeta metadata (ya no se usa).
Toda la información ahora se guarda directamente en la base de datos.
"""

import os
import shutil
import sys


def eliminar_metadata():
    """Elimina la carpeta data/metadata si existe"""
    try:
        # Ruta a la carpeta metadata
        project_root = os.path.dirname(os.path.abspath(__file__))
        metadata_path = os.path.join(project_root, 'data', 'metadata')
        
        if not os.path.exists(metadata_path):
            print("[OK] La carpeta metadata no existe (ya fue eliminada o nunca existió)")
            return True
        
        # Verificar si tiene archivos
        archivos = os.listdir(metadata_path)
        
        print("\n" + "="*70)
        print("[TRASH]  ELIMINAR CARPETA METADATA")
        print("="*70)
        
        print(f"\n[FOLDER] Carpeta encontrada: {metadata_path}")
        
        if archivos:
            print(f"\n[FILE] Archivos dentro ({len(archivos)}):")
            for archivo in archivos:
                archivo_path = os.path.join(metadata_path, archivo)
                if os.path.isfile(archivo_path):
                    size = os.path.getsize(archivo_path)
                    print(f"   - {archivo} ({size:,} bytes)")
                else:
                    print(f"   - {archivo}/ (carpeta)")
        else:
            print("\n[FILE] La carpeta está vacía")
        
        print("\n[WARN]  ADVERTENCIA:")
        print("   Esta carpeta ya NO se usa en el nuevo sistema.")
        print("   Toda la información ahora se guarda en la base de datos.")
        print("   Es seguro eliminarla.")
        
        respuesta = input("\n¿Deseas eliminar la carpeta metadata? (s/n): ").strip().lower()
        
        if respuesta in ['s', 'si', 'sí', 'yes', 'y']:
            print(f"\n[TRASH]  Eliminando {metadata_path}...")
            shutil.rmtree(metadata_path)
            print("[OK] Carpeta eliminada exitosamente!")
            
            print("\n[LIST] Beneficios:")
            print("   [OK] Espacio en disco liberado")
            print("   [OK] Menor complejidad del proyecto")
            print("   [OK] Todos los datos en un solo lugar (BD)")
            
            return True
        else:
            print("\n[ERR] Operación cancelada - La carpeta no fue eliminada")
            return False
            
    except PermissionError:
        print(f"\n[ERR] Error: No tienes permisos para eliminar la carpeta")
        print("   Intenta ejecutar como administrador")
        return False
    except Exception as e:
        print(f"\n[ERR] Error al eliminar carpeta: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print("\n" + "[MUSIC]"*35)
    print("ELIMINAR CARPETA METADATA (OBSOLETA)")
    print("[MUSIC]"*35)
    
    print("\n[LIST] Información:")
    print("   - La carpeta data/metadata/ ya NO se usa")
    print("   - Los archivos spotify_metadata.json y youtube_metadata.json son obsoletos")
    print("   - Todo ahora se guarda en la base de datos como JSON")
    print("   - Las imágenes se guardan como BLOB en la BD")
    
    resultado = eliminar_metadata()
    
    if resultado:
        print("\n" + "="*70)
        print("[OK] PROCESO COMPLETADO")
        print("="*70)
    
    print("\n[TIP] Para más información, consulta:")
    print("   - ELIMINACION_METADATA.md")
    print("   - ejemplos_playlist_json_completa.py")
    print("   - documentation/json_database_usage.md")
    
    input("\n[Presiona ENTER para salir]")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN]  Operación cancelada por el usuario")
        sys.exit(0)
