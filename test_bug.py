#!/usr/bin/env python
"""Test para reproducir el bug"""

import sys
sys.path.insert(0, 'pila_api/renderers/fixed_width')

from base import FixedWidthLine

# Crear una línea de 693 caracteres
l = FixedWidthLine(693)

# Escribir "TEST" en posiciones 687-690 (4 caracteres)
l.set_alpha(687, 690, "TEST")

linea = l.render()

print(f"Longitud: {len(linea)}")
print()

# Ver posiciones 680-693
print("Posiciones 680-693:")
for i in range(679, 693):
    char = linea[i]
    print(f"  Pos {i+1}: [{char}]")
