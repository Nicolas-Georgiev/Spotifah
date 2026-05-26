#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de migración para actualizar la base de datos existente.
Agrega las nuevas columnas necesarias para el sistema de playlists JSON completas.
"""

import os
import sys
import sqlite3


def migrar_base_datos():
    """Migra la base de datos existente agregando las nuevas columnas"""
    try:
        # Ruta a la base de datos
        project_root = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(project_root, 'data', 'BDD', 'ekho.db')
        
        if not os.path.exists(db_path):
            print(f"[ERR] No se encontró la base de datos en: {db_path}")
            print("   La BD se creará automáticamente al ejecutar el programa.")
            return False
        
        print("\n" + "="*70)
        print("[SYNC] MIGRACIÓN DE BASE DE DATOS")
        print("="*70)
        
        print(f"\n[FOLDER] Base de datos: {db_path}")
        
        # Conectar a la BD
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cambios_realizados = []
        
        # 1. Verificar y agregar caratula_blob a canciones
        print("\n[1/3] Verificando tabla 'canciones'...")
        cur.execute("PRAGMA table_info(canciones)")
        columnas_canciones = [col['name'] for col in cur.fetchall()]
        
        if 'caratula_blob' not in columnas_canciones:
            print("   [WARN]  Columna 'caratula_blob' no existe, agregando...")
            cur.execute("ALTER TABLE canciones ADD COLUMN caratula_blob BLOB")
            cambios_realizados.append("Agregada columna 'caratula_blob' a tabla 'canciones'")
            print("   [OK] Columna 'caratula_blob' agregada")
        else:
            print("   [OK] Columna 'caratula_blob' ya existe")
        
        # 2. Verificar y agregar playlist_json a playlists
        print("\n[2/3] Verificando tabla 'playlists'...")
        cur.execute("PRAGMA table_info(playlists)")
        columnas_playlists = [col['name'] for col in cur.fetchall()]
        
        if 'playlist_json' not in columnas_playlists:
            print("   [WARN]  Columna 'playlist_json' no existe, agregando...")
            cur.execute("ALTER TABLE playlists ADD COLUMN playlist_json TEXT")
            cambios_realizados.append("Agregada columna 'playlist_json' a tabla 'playlists'")
            print("   [OK] Columna 'playlist_json' agregada")
        else:
            print("   [OK] Columna 'playlist_json' ya existe")
        
        # 3. Verificar y agregar caratula_blob a playlists
        print("\n[3/3] Verificando carátula en 'playlists'...")
        if 'caratula_blob' not in columnas_playlists:
            print("   [WARN]  Columna 'caratula_blob' no existe, agregando...")
            cur.execute("ALTER TABLE playlists ADD COLUMN caratula_blob BLOB")
            cambios_realizados.append("Agregada columna 'caratula_blob' a tabla 'playlists'")
            print("   [OK] Columna 'caratula_blob' agregada")
        else:
            print("   [OK] Columna 'caratula_blob' ya existe")
        
        # Guardar cambios
        conn.commit()
        conn.close()
        
        # Resumen
        print("\n" + "="*70)
        if cambios_realizados:
            print("[OK] MIGRACIÓN COMPLETADA - Cambios realizados:")
            print("="*70)
            for i, cambio in enumerate(cambios_realizados, 1):
                print(f"   {i}. {cambio}")
        else:
            print("[OK] BASE DE DATOS YA ACTUALIZADA")
            print("="*70)
            print("   No se necesitaron cambios, la BD ya tiene todas las columnas.")
        
        print("\n[LIST] Estado de las tablas:")
        print("   [OK] canciones.caratula_blob (BLOB)")
        print("   [OK] playlists.playlist_json (TEXT)")
        print("   [OK] playlists.caratula_blob (BLOB)")
        
        print("\n[TIP] Ahora puedes ejecutar:")
        print("   python test_playlist_json_completa.py")
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n[ERR] Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"\n[ERR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Función principal"""
    print("\n" + "[MUSIC]"*35)
    print("MIGRACIÓN DE BASE DE DATOS - Playlists JSON Completas")
    print("[MUSIC]"*35)
    
    print("\n[LIST] Esta migración agregará las siguientes columnas:")
    print("   - canciones.caratula_blob (BLOB)")
    print("   - playlists.playlist_json (TEXT)")
    print("   - playlists.caratula_blob (BLOB)")
    
    print("\n[WARN]  IMPORTANTE:")
    print("   - Esta operación es segura y no elimina datos existentes")
    print("   - El proceso es rápido y no afecta datos existentes")
    
    # Ejecutar directamente sin pedir confirmación
    print("\n[SYNC] Iniciando migración...")
    exito = migrar_base_datos()
    
    if not exito:
        print("\n[WARN]  La migración no se completó correctamente")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[WARN]  Operación cancelada por el usuario")
        sys.exit(0)
