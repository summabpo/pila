# pila_api/views.py

import json
from datetime import date, datetime

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse

from rest_framework import status
from rest_framework.decorators import api_view

from .models import PilaPlanilla, PilaPlanillaDetalle, PilaNovedad
from .serializers import PayloadPlanillaSerializer
from .services.calcular_planilla import calcular_planilla
from .services.generar_txt import generar_txt_planilla
from .dto import planilla_to_response


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _require_service_token(request):
    """
    Enforce internal service-to-service auth via:
    Authorization: Bearer <PILA_SERVICE_TOKEN>
    """
    expected = getattr(settings, "PILA_SERVICE_TOKEN", "")
    if not expected:
        return JsonResponse(
            {"detail": "PILA_SERVICE_TOKEN no está configurado"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    auth = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION", "")
    if not auth.startswith("Bearer "):
        return JsonResponse({"detail": "Missing Bearer token"}, status=401)

    token = auth.replace("Bearer ", "").strip()
    if token != expected:
        return JsonResponse({"detail": "Invalid token"}, status=401)

    return None


def _to_date(value):
    if value is None:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value)
    raise TypeError(f"Tipo de fecha no soportado: {type(value)}")


def json_safe(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_safe(v) for v in value]
    return value


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------

@api_view(["POST"])
def crear_planilla(request):
    """
    POST /api/v1/pila/planillas/
    Crea o reutiliza una planilla y genera sus detalles + novedades
    """
    auth_error = _require_service_token(request)
    if auth_error:
        return auth_error

    serializer = PayloadPlanillaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    payload = serializer.validated_data

    empresa = payload["empresa"]
    planilla_data = payload["planilla"]
    empleados = payload.get("empleados", [])

    if not empleados:
        return JsonResponse({"detail": "Payload sin empleados"}, status=400)

    numero_interno = planilla_data["numero_interno"]

    obj, created = PilaPlanilla.objects.get_or_create(
    numero_interno=numero_interno,
    defaults={
        "periodo": payload["periodo"],
        "empresa_nit": empresa["nit"],
        "empresa_sucursal": empresa["sucursal"],
        "estado": "EN_PROCESO",
        "payload_inicial": request.data,
        "totales": None,
        "resumen": {
            "empleados_procesados": 0,
            "empleados_con_error": 0,
            "warnings": 0,
        },
        "errores": [],
        "tiene_archivo": False,
    }
)

    # 🔑 Forzar actualización del payload SIEMPRE
    obj.payload_inicial = request.data
    obj.errores = []
    obj.estado = "EN_PROCESO"
    obj.save(update_fields=["payload_inicial", "errores", "estado"])
    
    force = request.GET.get("force") == "1"

    ya_tiene_detalles = PilaPlanillaDetalle.objects.filter(planilla=obj).exists()

    if force or created or not ya_tiene_detalles:
        riesgo_arl_default = str(empresa.get("clase_riesgo_arl", "1"))

        with transaction.atomic():
            # limpieza segura
            PilaNovedad.objects.filter(detalle__planilla=obj).delete()
            PilaPlanillaDetalle.objects.filter(planilla=obj).delete()

            for emp in empleados:
                tipo_doc = emp.get("tipo_doc", "")
                numero_doc = emp.get("numero_doc") or emp.get("num_doc") or ""

                # Clase de riesgo (campo 78, pos 513): por empleado desde payload, según tarifa ARL
                riesgo_arl = str(emp.get("clase_riesgo") or riesgo_arl_default).strip() or riesgo_arl_default
                if riesgo_arl not in ("1", "2", "3", "4", "5"):
                    riesgo_arl = riesgo_arl_default

                # Extraer datos comunes del empleado
                nombre = (emp.get("nombre_completo") or "").strip()
                partes = [p for p in nombre.split() if p]
                primer_apellido = partes[0] if len(partes) >= 1 else ""
                primer_nombre = partes[1] if len(partes) >= 2 else ""

                tipo_cotizante = emp.get("tipo_cotizante", "")
                subtipo_cotizante = emp.get("subtipo_cotizante", "00")
                entidades = emp.get("entidades", {})
                caja_compensacion = bool(entidades.get("caja"))

                # ============================================
                # NUEVO: Procesar múltiples registros por empleado
                # ============================================
                registros = emp.get("registros", [])
                
                # Si no hay registros (formato antiguo), crear uno con datos del empleado
                if not registros:
                    dias = emp.get("dias", {}) or {}
                    ibc = emp.get("ibc", {})
                    registros = [{
                        "tipo_linea": "NORMAL",
                        "dias": dias,
                        "ibc": ibc,
                        "novedades": emp.get("novedades", [])
                    }]
                
                # Crear un detalle por cada registro (línea tipo 02)
                for registro in registros:
                    dias = registro.get("dias", {}) or {}
                    dias_salud = int(dias.get("salud", 0) or 0)
                    dias_pension = int(dias.get("pension", 0) or 0)
                    dias_arl = int(dias.get("arl", 0) or 0)
                    dias_caja = int(dias.get("caja", 0) or 0)

                    # mantenemos dias_cotizados como "principal" usando salud
                    dias_cotizados = dias_salud

                    ibc = registro.get("ibc", {})
                    ibc_salud = ibc.get("salud", 0)
                    ibc_pension = ibc.get("pension", 0)
                    ibc_arl = ibc.get("arl", 0)

                    detalle = PilaPlanillaDetalle.objects.create(
                        planilla=obj,
                        tipo_doc=tipo_doc,
                        numero_doc=numero_doc,
                        primer_nombre=primer_nombre,
                        primer_apellido=primer_apellido,
                        tipo_cotizante=tipo_cotizante,
                        subtipo_cotizante=subtipo_cotizante,

                        dias_cotizados=dias_cotizados,
                        dias_salud=dias_salud,
                        dias_pension=dias_pension,
                        dias_arl=dias_arl,
                        dias_caja=dias_caja,

                        ibc=ibc_salud,
                        ibc_salud=ibc_salud,
                        ibc_pension=ibc_pension,
                        ibc_arl=ibc_arl,
                        riesgo_arl=riesgo_arl,
                        caja_compensacion=caja_compensacion,
                        estado="OK",
                        errores=[],
                    )

                    # Crear novedades para este registro específico
                    for nov in registro.get("novedades", []):
                        codigo = (nov.get("codigo") or "").upper()
                        if not codigo:
                            continue

                        fi = _to_date(nov.get("fecha_desde"))
                        ff = _to_date(nov.get("fecha_hasta"))

                        if not fi:
                            continue

                        PilaNovedad.objects.create(
                            detalle=detalle,
                            tipo_novedad=codigo,
                            fecha_inicio=fi,
                            fecha_fin=ff,
                            dias=nov.get("dias"),
                            valor=nov.get("valor"),
                            metadata=json_safe(nov),
                        )

        # cálculo SOLO una vez
        calcular_planilla(obj.planilla_id)
        obj.refresh_from_db()

    return JsonResponse(
        planilla_to_response(obj),
        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
    )


@api_view(["GET"])
def consultar_planilla(request, planilla_id: int):
    auth_error = _require_service_token(request)
    if auth_error:
        return auth_error

    try:
        obj = PilaPlanilla.objects.get(planilla_id=planilla_id)
    except PilaPlanilla.DoesNotExist:
        return JsonResponse({"detail": "No existe"}, status=404)

    return JsonResponse(planilla_to_response(obj), status=200)


@api_view(["GET"])
def listar_detalles(request, planilla_id: int):
    auth_error = _require_service_token(request)
    if auth_error:
        return auth_error

    try:
        planilla = PilaPlanilla.objects.get(planilla_id=planilla_id)
    except PilaPlanilla.DoesNotExist:
        return JsonResponse({"detail": "No existe"}, status=404)

    detalles = (
        PilaPlanillaDetalle.objects
        .filter(planilla=planilla)
        .prefetch_related("novedades")
        .order_by("id")
    )

    data = {
        "planilla": planilla_to_response(planilla),
        "detalles": [],
    }

    for d in detalles:
        data["detalles"].append({
            "detalle_id": d.id,
            "tipo_doc": d.tipo_doc,
            "numero_doc": d.numero_doc,
            "primer_nombre": d.primer_nombre,
            "primer_apellido": d.primer_apellido,
            "tipo_cotizante": d.tipo_cotizante,
            "subtipo_cotizante": d.subtipo_cotizante,
            "dias_cotizados": d.dias_cotizados,
            "dias_salud": d.dias_salud,
            "dias_pension": d.dias_pension,
            "dias_arl": d.dias_arl,
            "dias_caja": d.dias_caja,
            "ibc": str(d.ibc),
            "ibc_salud": str(d.ibc_salud),
            "ibc_pension": str(d.ibc_pension),
            "ibc_arl": str(d.ibc_arl),
            "riesgo_arl": d.riesgo_arl,
            "caja_compensacion": d.caja_compensacion,
            "estado": d.estado,
            "errores": d.errores,
            "aportes": d.aportes,
            "aportes_empleado": str(d.aportes_empleado),
            "aportes_empleador": str(d.aportes_empleador),
            "novedades": [
                {
                    "id": n.id,
                    "tipo_novedad": n.tipo_novedad,
                    "fecha_inicio": n.fecha_inicio.isoformat(),
                    "fecha_fin": n.fecha_fin.isoformat() if n.fecha_fin else None,
                    "dias": n.dias,
                    "valor": str(n.valor) if n.valor else None,
                    "metadata": n.metadata,
                }
                for n in d.novedades.all().order_by("id")
            ],
        })

    return JsonResponse(data, status=200)


@api_view(["POST"])
def calcular_planilla_view(request, planilla_id: int):
    """
    POST /api/v1/pila/planillas/{planilla_id}/calcular/
    """
    auth_error = _require_service_token(request)
    if auth_error:
        return auth_error

    try:
        PilaPlanilla.objects.get(planilla_id=planilla_id)
    except PilaPlanilla.DoesNotExist:
        return JsonResponse({"detail": "Planilla no existe"}, status=404)

    resumen = calcular_planilla(planilla_id)

    return JsonResponse(
        {"planilla_id": planilla_id, "resultado": resumen},
        status=200,
    )


@api_view(["GET"])
def descargar_archivo(request, planilla_id: int):
    """
    GET /api/v1/pila/planillas/{planilla_id}/archivo/
    Genera y descarga el archivo TXT PILA completo para la planilla.
    """
    auth_error = _require_service_token(request)
    if auth_error:
        return auth_error

    try:
        planilla = PilaPlanilla.objects.get(planilla_id=planilla_id)
    except PilaPlanilla.DoesNotExist:
        return JsonResponse({"detail": "Planilla no existe"}, status=404)

    # Validar que la planilla tenga detalles válidos
    detalles_ok = PilaPlanillaDetalle.objects.filter(
        planilla=planilla, 
        estado="OK"
    ).count()
    
    if detalles_ok == 0:
        return JsonResponse(
            {"detail": "La planilla no tiene detalles válidos para generar el archivo"},
            status=400
        )

    # Parámetro opcional: tipo_planilla=K (solo estudiantes) o E (solo no estudiantes)
    tipo_planilla = request.GET.get("tipo_planilla", "").strip().upper()
    filtro = tipo_planilla if tipo_planilla in ("K", "E") else None

    try:
        # Generar el archivo TXT (filtrado por tipo si se especifica)
        contenido_txt = generar_txt_planilla(planilla_id, filtro_tipo_planilla=filtro)
        
        # Validar longitudes de cada línea antes de enviar
        lineas = contenido_txt.split('\n')
        if len(lineas[0]) != 359:
            raise ValueError(f"Registro 01 tiene {len(lineas[0])} caracteres, esperado 359")
        
        for i in range(1, len(lineas)):
            if len(lineas[i]) != 693:
                raise ValueError(f"Registro 02 línea {i} tiene {len(lineas[i])} caracteres, esperado 693")
        
        # Preparar nombre de archivo (incluir sufijo tipo cuando se filtra)
        sufijo = f"_{filtro}" if filtro else ""
        nombre_archivo = f"PILA_{planilla.numero_interno}{sufijo}.txt"
        
        # Crear respuesta HTTP con el archivo
        # IMPORTANTE: Usar ISO-8859-1 (Latin-1) para que caracteres especiales ocupen 1 byte
        response = HttpResponse(contenido_txt, content_type='text/plain; charset=iso-8859-1')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
        response['Content-Length'] = len(contenido_txt.encode('iso-8859-1'))
        
        return response
        
    except ValueError as e:
        return JsonResponse(
            {"detail": f"Error al generar archivo: {str(e)}"},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {"detail": f"Error interno: {str(e)}"},
            status=500
        )