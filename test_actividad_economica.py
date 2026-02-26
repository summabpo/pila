#!/usr/bin/env python
"""Script para probar el campo de actividad económica"""

import sys
import os
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pila_project.settings')
django.setup()

from pila_api.renderers.fixed_width.registro_02 import Registro02Renderer

# Crear un data mínimo con actividad económica
data = {
    "secuencia": "00043",
    "tipo_doc": "CC",
    "num_doc": "79623700",
    "tipo_cotizante": "01",
    "subtipo_cotizante": "00",
    "municipio": "08001",
    "papellido": "PIÑEROS",
    "sapellido": "ABRIL",
    "pnombre": "ALEXANDER",
    "snombre": "no data",
    "vst": "",
    "irl_dias": 0,
    "afp": "00230301",
    "eps": "EPS002",
    "ccf": "CCF07",
    "dias_salud": 30,
    "dias_pension": 30,
    "dias_arl": 30,
    "dias_caja": 30,
    "v_192_200": 4377262,
    "tipo_salario": "F",
    "ibc_pension": 4050200,
    "v_210_218": 4050200,
    "v_219_227": 4050200,
    "v_228_236": 4050200,
    "v_237_245": "0.16000",
    "v_246_254": 648032,
    "v_255_263": 0,
    "v_264_272": 0,
    "v_273_281": 0,
    "v_282_290": 0,
    "v_291_299": 0,
    "v_300_308": 0,
    "v_309_317": "0.12500",
    "v_318_326": 162008,
    "v_327_332": 0,
    "tarifa_arl": "0.0435000",
    "centro_trabajo": 0,
    "cotizacion_arl": 98662,
    "tarifa_ccf": "0.04000",
    "valor_ccf": 0,
    "tarifa_sena": "0.02000",
    "valor_sena": 0,
    "tarifa_icbf": "0.03000",
    "valor_icbf": 0,
    "exonerado": "S",
    "codigo_arl": "14-11",
    "clase_riesgo": "3",
    "actividad_economica_arl": "4522901",  # 7 caracteres
    "raw_333_693": None,
}

renderer = Registro02Renderer()
linea = renderer.render(data)

print(f"Longitud de la línea: {len(linea)}")
print(f"Esperado: 693")
print(f"Diferencia: {len(linea) - 693}")
print()

if len(linea) != 693:
    print("❌ ERROR: La línea no tiene 693 caracteres")
    print()
    print(f"Últimos 20 caracteres: [{linea[-20:]}]")
    print(f"Actividad económica (pos 687-693): [{linea[686:693]}]")
    if len(linea) > 693:
        print(f"Carácter extra en pos {694}: [{linea[693]}]")
else:
    print("✓ OK: La línea tiene 693 caracteres")
