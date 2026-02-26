# pila_api/utils/redondeos.py
"""
Utilidades de redondeo según Decreto 1990 de 2016 (Colombia).

Reglas:
- IBC: se aproxima al peso superior más cercano (redondeo hacia arriba)
- Cotizaciones: se ajustan al múltiplo de 100 superior (redondeo hacia arriba a centenas)
"""

from decimal import Decimal, ROUND_CEILING
from math import ceil


def redondear_ibc(valor: Decimal | float | int | str) -> int:
    """
    Redondea el IBC al peso superior más cercano según Decreto 1990 de 2016.
    
    Ejemplos:
        - 1234.50 -> 1235
        - 1234.01 -> 1235
        - 1234.00 -> 1234
        - 1234.99 -> 1235
    
    Args:
        valor: Valor del IBC a redondear
        
    Returns:
        IBC redondeado hacia arriba al entero más cercano
    """
    if valor is None:
        return 0
    
    # Convertir a Decimal para precisión
    if isinstance(valor, str):
        valor_decimal = Decimal(valor)
    elif isinstance(valor, (int, float)):
        valor_decimal = Decimal(str(valor))
    elif isinstance(valor, Decimal):
        valor_decimal = valor
    else:
        return 0
    
    # Redondear hacia arriba usando math.ceil (más preciso que Decimal con ROUND_CEILING)
    # Convertir a float para usar ceil, luego a int
    valor_float = float(valor_decimal)
    return int(ceil(valor_float))


def redondear_cotizacion(valor: Decimal | float | int | str) -> int:
    """
    Redondea la cotización al múltiplo de 100 superior según Decreto 1990 de 2016.
    
    Ejemplos:
        - 899470 -> 899500
        - 580065 -> 580100
        - 224867 -> 224900
        - 100000 -> 100000 (ya es múltiplo de 100)
        - 100001 -> 100100
    
    Args:
        valor: Valor de la cotización a redondear
        
    Returns:
        Cotización redondeada hacia arriba al múltiplo de 100 superior
    """
    if valor is None:
        return 0
    
    # Convertir a Decimal para precisión
    if isinstance(valor, str):
        valor_decimal = Decimal(valor)
    elif isinstance(valor, (int, float)):
        valor_decimal = Decimal(str(valor))
    elif isinstance(valor, Decimal):
        valor_decimal = valor
    else:
        return 0
    
    # Convertir a float para usar ceil
    valor_float = float(valor_decimal)
    
    # Redondear hacia arriba al múltiplo de 100 superior
    # Dividir por 100, redondear hacia arriba, multiplicar por 100
    valor_redondeado = ceil(valor_float / 100) * 100
    
    return int(valor_redondeado)
