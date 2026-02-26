# pila_api/dto.py

def planilla_to_response(planilla):
    return {
        "planilla_id": planilla.planilla_id,
        "numero_interno": planilla.numero_interno,
        "estado": planilla.estado,
        "periodo": planilla.periodo,
        "empresa": {
            "nit": planilla.empresa_nit,
            "sucursal": planilla.empresa_sucursal,
        },
        "totales": planilla.totales,
        "resumen": planilla.resumen or {
            "empleados_procesados": 0,
            "empleados_con_error": 0,
            "warnings": 0,
        },
        "errores": planilla.errores or [],
        "tiene_archivo": bool(planilla.tiene_archivo),
    }