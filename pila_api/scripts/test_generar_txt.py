#!/usr/bin/env python
# pila_api/scripts/test_generar_txt.py
"""
Script de prueba para generar_txt_planilla()
Genera el archivo TXT completo para la planilla ID 1
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pila_service.settings")
django.setup()

from pila_api.services.generar_txt import generar_txt_planilla
from pila_api.models import PilaPlanilla


def main():
    planilla_id = 1
    
    print(f"=" * 80)
    print(f"Prueba de generación de TXT PILA - Planilla ID {planilla_id}")
    print(f"=" * 80)
    print()
    
    try:
        # Verificar que existe la planilla
        planilla = PilaPlanilla.objects.get(planilla_id=planilla_id)
        print(f"✓ Planilla encontrada:")
        print(f"  - Número interno: {planilla.numero_interno}")
        print(f"  - Periodo: {planilla.periodo}")
        print(f"  - Estado: {planilla.estado}")
        print(f"  - NIT: {planilla.empresa_nit}")
        print(f"  - Detalles: {planilla.detalles.count()} empleados")
        print(f"  - Detalles OK: {planilla.detalles.filter(estado='OK').count()}")
        print()
        
        # Generar TXT
        print("Generando archivo TXT...")
        contenido_txt = generar_txt_planilla(planilla_id)
        
        # Analizar resultado
        lineas = contenido_txt.split("\n")
        print(f"✓ Archivo generado exitosamente")
        print(f"  - Total de líneas: {len(lineas)}")
        print(f"  - Línea 01 (encabezado): 1")
        print(f"  - Líneas 02 (detalles): {len(lineas) - 1}")
        print()
        
        # Validar longitudes
        print("Validando longitudes:")
        linea_01 = lineas[0] if lineas else ""
        print(f"  - Línea 01: {len(linea_01)} caracteres (esperado: 359)")
        
        if len(lineas) > 1:
            linea_02_primera = lineas[1]
            print(f"  - Primera línea 02: {len(linea_02_primera)} caracteres (esperado: 693)")
            
            # Verificar todas las líneas 02
            longitudes_02 = [len(l) for l in lineas[1:]]
            if all(l == 693 for l in longitudes_02):
                print(f"  ✓ Todas las líneas 02 tienen 693 caracteres")
            else:
                print(f"  ✗ ERROR: No todas las líneas 02 tienen 693 caracteres")
                for idx, long in enumerate(longitudes_02, start=1):
                    if long != 693:
                        print(f"    - Línea 02 #{idx}: {long} caracteres")
        print()
        
        # Mostrar muestra de la línea 01
        print("Muestra de línea 01 (encabezado):")
        print(f"  [1-80]: {linea_01[:80]}")
        print(f"  [200-280]: {linea_01[199:280] if len(linea_01) >= 280 else '(incompleto)'}")
        print(f"  [280-359]: {linea_01[279:] if len(linea_01) >= 280 else '(incompleto)'}")
        print()
        
        # Mostrar muestra de la primera línea 02
        if len(lineas) > 1:
            print("Muestra de primera línea 02 (detalle):")
            linea_02 = lineas[1]
            print(f"  [1-50]: {linea_02[:50]}")
            print(f"  [30-110]: {linea_02[29:110]}")  # Nombres
            print(f"  [150-200]: {linea_02[149:200]}")  # Entidades
            print()
        
        # Guardar archivo de prueba
        output_path = os.path.join(
            os.path.dirname(__file__),
            f"test_output_planilla_{planilla_id}.txt"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(contenido_txt)
        
        print(f"✓ Archivo guardado en: {output_path}")
        print()
        
        # Resumen
        print("=" * 80)
        print("RESUMEN:")
        print(f"  ✓ Archivo TXT generado correctamente")
        print(f"  ✓ {len(lineas)} líneas totales")
        print(f"  ✓ Longitud línea 01: {len(linea_01)}/359")
        if len(lineas) > 1:
            print(f"  ✓ Longitud líneas 02: {len(lineas[1])}/693")
        print("=" * 80)
        
    except PilaPlanilla.DoesNotExist:
        print(f"✗ ERROR: No existe la planilla con ID {planilla_id}")
        print()
        print("Planillas disponibles:")
        for p in PilaPlanilla.objects.all():
            print(f"  - ID {p.planilla_id}: {p.numero_interno} ({p.periodo})")
        sys.exit(1)
        
    except Exception as e:
        print(f"✗ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
