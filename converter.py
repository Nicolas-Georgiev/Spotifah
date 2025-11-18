#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de acceso directo al conversor
Ejecuta el conversor que está en src/
"""

import os
import sys

# Añadir src al path y ejecutar el conversor
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_dir)

# Cambiar al directorio src para ejecutar desde allí
os.chdir(src_dir)

# Importar y ejecutar
from run_converter import main

if __name__ == "__main__":
    main()
