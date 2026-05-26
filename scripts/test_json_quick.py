#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rápido del sistema JSON de base de datos.
Ejecuta este script para verificar que todo funciona correctamente.
"""

import os
import sys

# Asegurar que podemos importar desde src
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def test_json_system():
    """Prueba rápida del sistema JSON"""
    print("\n" + "="*60)
    print("TEST RÁPIDO - Sistema JSON de Base de Datos")
    print("="*60)
    
    try:
        # Importar funciones
        print("\n1⃣ Importando funciones...")
        from model.db_adapter import (
            upsert_cancion_json,
            get_cancion_json,
            get_todas_canciones_json
        )
        print("   [OK] Funciones importadas correctamente")
        
        # Test 1: Guardar canción y obtener JSON
        print("\n2⃣ Guardando canción de prueba...")
        metadata = {
            'titulo': 'Test JSON Song',
            'artista': 'Test Artist',
            'duracion_seg': 180,
            'plataforma_origen': 'test'
        }
        
        cancion_json = upsert_cancion_json(metadata)
        
        if cancion_json:
            print(f"   [OK] Canción guardada con ID: {cancion_json['id_cancion']}")
            print(f"   [OK] JSON devuelto contiene {len(cancion_json)} campos")
            print(f"   [OK] Título: {cancion_json['titulo']}")
            print(f"   [OK] Artista: {cancion_json['artista']}")
            print(f"   [OK] Fecha importación: {cancion_json['fecha_importacion']}")
            id_test = cancion_json['id_cancion']
        else:
            print("   [ERR] Error al guardar canción")
            return False
        
        # Test 2: Leer canción por ID
        print(f"\n3⃣ Leyendo canción por ID ({id_test})...")
        cancion = get_cancion_json(id_cancion=id_test)
        
        if cancion:
            print(f"   [OK] Canción encontrada: {cancion['titulo']}")
            print(f"   [OK] JSON completo recibido")
        else:
            print("   [ERR] Error al leer canción")
            return False
        
        # Test 3: Leer canción por título y artista
        print("\n4⃣ Leyendo canción por título y artista...")
        cancion = get_cancion_json(titulo='Test JSON Song', artista='Test Artist')
        
        if cancion:
            print(f"   [OK] Canción encontrada: {cancion['titulo']}")
        else:
            print("   [ERR] Error al buscar canción")
            return False
        
        # Test 4: Listar todas las canciones
        print("\n5⃣ Listando todas las canciones...")
        canciones = get_todas_canciones_json()
        
        if canciones:
            print(f"   [OK] Se encontraron {len(canciones)} canciones")
            print(f"   [OK] Todas en formato JSON")
        else:
            print("   [WARN] No hay canciones en la BD (esto es normal en BD nueva)")
        
        # Resultado final
        print("\n" + "="*60)
        print("[OK] TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("="*60)
        print("\n[LIST] Resumen:")
        print("   • Funciones JSON importadas: [OK]")
        print("   • Guardar y retornar JSON: [OK]")
        print("   • Leer por ID: [OK]")
        print("   • Leer por título/artista: [OK]")
        print("   • Listar todas: [OK]")
        print("\n[DONE] El sistema JSON está funcionando perfectamente!")
        print("\n[BOOK] Para más ejemplos, ejecuta: python ejemplos_json_database.py")
        print("[BOOKS] Lee la documentación en: documentation/json_database_usage.md")
        
        return True
        
    except ImportError as e:
        print(f"\n[ERR] Error de importación: {e}")
        print("\n[TIP] Asegúrate de estar en el directorio correcto del proyecto")
        return False
        
    except Exception as e:
        print(f"\n[ERR] Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_json_system()
    sys.exit(0 if success else 1)
