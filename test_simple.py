#!/usr/bin/env python
"""Script simple para probar el renderer"""

import sys
sys.path.insert(0, 'pila_api/renderers/fixed_width')

from base import FixedWidthLine

# Crear una línea de 693 caracteres
l = FixedWidthLine(693)

# Escribir actividad económica en posiciones 687-693 (7 caracteres)
actividad = "4522901"
print(f"Valor a escribir: [{actividad}]")
print(f"Longitud: {len(actividad)}")
print(f"Posiciones: 687-693 (ancho: {693 - 687 + 1})")
print()

l.set_alpha(687, 693, actividad)

linea = l.render()

print(f"Longitud de la línea: {len(linea)}")
print(f"Esperado: 693")
print()

if len(linea) == 693:
    print("✓ OK: La línea tiene 693 caracteres")
    print(f"Actividad económica (pos 687-693): [{linea[686:693]}]")
else:
    print(f"❌ ERROR: La línea tiene {len(linea)} caracteres")
