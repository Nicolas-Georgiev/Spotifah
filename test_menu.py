#!/usr/bin/env python3
# test_menu.py
"""Prueba simple del menú principal"""

import sys

def test_menu():
    """Prueba simple del menú"""
    print("=== PRUEBA DE MENÚ ===")
    print("📋 OPCIONES:")
    print("  1️⃣  Opción 1")
    print("  2️⃣  Opción 2") 
    print("  0️⃣  Salir")
    print("=" * 50)
    
    while True:
        try:
            print("\nSelecciona una opción (1-2, 0 para salir): ", end='', flush=True)
            choice = input().strip()
            print(f"DEBUG: Recibido '{choice}' (longitud: {len(choice)})")
            
            if choice == '0':
                print("👋 Saliendo...")
                break
            elif choice == '1':
                print("✅ Seleccionaste opción 1")
                continue
            elif choice == '2':
                print("✅ Seleccionaste opción 2")
                continue
            else:
                print(f"❌ Opción no válida: '{choice}'")
                continue
                
        except EOFError:
            print("\n❌ EOF detectado - stdin cerrado")
            break
        except KeyboardInterrupt:
            print("\n❌ Interrumpido por usuario")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    print("🧪 Iniciando prueba de menú...")
    print(f"stdin.isatty(): {sys.stdin.isatty()}")
    print(f"stdout.isatty(): {sys.stdout.isatty()}")
    test_menu()