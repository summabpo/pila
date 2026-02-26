# pila_api/services/calcular_planilla.py

from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from pila_api.models import PilaPlanilla, PilaPlanillaDetalle
from pila_api.utils.redondeos import redondear_cotizacion, redondear_ibc

D0 = Decimal("0")
Q2 = Decimal("0.01")

# Tasas v0.2 (mínimas)
TASA_SALUD_EMP = Decimal("0.04")
TASA_SALUD_EMPL = Decimal("0.085")

TASA_PENSION_EMP = Decimal("0.04")
TASA_PENSION_EMPL = Decimal("0.12")

TASA_CAJA = Decimal("0.04")

ARL_TASAS = {
    "1": Decimal("0.00522"),
    "2": Decimal("0.01044"),
    "3": Decimal("0.02436"),
    "4": Decimal("0.04350"),
    "5": Decimal("0.06960"),
}


def _clamp(value: Decimal, min_v: Decimal, max_v: Decimal) -> Decimal:
    if value < min_v:
        return min_v
    if value > max_v:
        return max_v
    return value


def _to_decimal(x) -> Decimal:
    if x is None:
        return D0
    if isinstance(x, Decimal):
        return x
    return Decimal(str(x))


def _q2(x: Decimal) -> Decimal:
    return _to_decimal(x).quantize(Q2, rounding=ROUND_HALF_UP)


def _calc_pct(base: Decimal, pct: Decimal) -> Decimal:
    return _q2(_to_decimal(base) * _to_decimal(pct))


def _calcular_fsp(ibc_pension: Decimal, smmlv: Decimal, fsp_porcentajes: dict) -> tuple[Decimal, Decimal]:
    """
    Calcula Fondo Solidaridad Pensional (FSP) según Decreto 1990 de 2016.
    
    FSP se calcula cuando IBC > 4 SMLV.
    El porcentaje varía según el rango de SMLV:
    - 4-16 SMLV: porcentaje según fsp_porcentajes["4-16"]
    - 16-17 SMLV: porcentaje según fsp_porcentajes["16-17"]
    - 17-18 SMLV: porcentaje según fsp_porcentajes["17-18"]
    - 18-19 SMLV: porcentaje según fsp_porcentajes["18-19"]
    - 19-20 SMLV: porcentaje según fsp_porcentajes["19-20"]
    - >20 SMLV: porcentaje según fsp_porcentajes[">20"]
    
    Args:
        ibc_pension: IBC de pensión (salario + VST si aplica)
        smmlv: Salario Mínimo Legal Vigente
        fsp_porcentajes: Diccionario con porcentajes FSP por rango (en decimal, ej: 0.01 = 1%)
        
    Returns:
        Tuple (fsp_solidaridad, fsp_subsistencia) - ambos valores redondeados según Decreto 1990
    """
    if ibc_pension <= 0 or smmlv <= 0:
        return (D0, D0)
    
    # Calcular cuántos SMLV representa el IBC
    smlv_count = ibc_pension / smmlv
    
    # Si IBC <= 4 SMLV, no aplica FSP
    if smlv_count <= Decimal("4"):
        return (D0, D0)
    
    # Determinar porcentaje según rango
    porcentaje_fsp = D0
    if smlv_count <= Decimal("16"):
        porcentaje_fsp = Decimal(str(fsp_porcentajes.get("4-16", 0.01)))
    elif smlv_count <= Decimal("17"):
        porcentaje_fsp = Decimal(str(fsp_porcentajes.get("16-17", 0.012)))
    elif smlv_count <= Decimal("18"):
        porcentaje_fsp = Decimal(str(fsp_porcentajes.get("17-18", 0.014)))
    elif smlv_count <= Decimal("19"):
        porcentaje_fsp = Decimal(str(fsp_porcentajes.get("18-19", 0.016)))
    elif smlv_count <= Decimal("20"):
        porcentaje_fsp = Decimal(str(fsp_porcentajes.get("19-20", 0.018)))
    else:  # > 20
        porcentaje_fsp = Decimal(str(fsp_porcentajes.get(">20", 0.02)))
    
    # Calcular FSP sobre el IBC
    fsp_total = _calc_pct(ibc_pension, porcentaje_fsp)
    
    # FSP se divide en dos partes iguales: solidaridad y subsistencia
    fsp_solidaridad = fsp_total / Decimal("2")
    fsp_subsistencia = fsp_total / Decimal("2")
    
    # Redondear según Decreto 1990 (múltiplo de 100 superior)
    fsp_solidaridad_redondeado = Decimal(redondear_cotizacion(fsp_solidaridad))
    fsp_subsistencia_redondeado = Decimal(redondear_cotizacion(fsp_subsistencia))
    
    return (fsp_solidaridad_redondeado, fsp_subsistencia_redondeado)


def calcular_planilla(planilla_id: int) -> dict:
    with transaction.atomic():
        planilla = PilaPlanilla.objects.select_for_update().get(planilla_id=planilla_id)

        # --- Parámetros legales desde payload ---
        params = (planilla.payload_inicial or {}).get("parametros", {}) or {}

        smmlv = _to_decimal(params.get("smmlv"))
        tope_smmlv = _to_decimal(params.get("tope_ibc_smmlv", 25))
        dias_base = _to_decimal(params.get("dias_base", 30))
        fsp_porcentajes = params.get("fsp_porcentajes", {}) or {}
        # EPS desde conceptosfijos: idfijo 8 (empleado), idfijo 18 (empresa cuando IBC > 10 SMLV)
        tasa_salud_emp_param = _to_decimal(params.get("tasa_salud_emp", 0.04))
        tasa_salud_empl_ibc10_param = _to_decimal(params.get("tasa_salud_empl_ibc_mayor_10", 0.085))

        if smmlv <= 0:
            planilla.estado = "CON_ERRORES"
            planilla.errores = ["Falta parametros.smmlv en payload"]
            planilla.save(update_fields=["estado", "errores"])
            return {"resumen": planilla.resumen, "totales": planilla.totales, "estado": planilla.estado}

        ibc_max_global = _q2(smmlv * tope_smmlv)

        detalles = (
            PilaPlanillaDetalle.objects
            .filter(planilla=planilla)
            .prefetch_related("novedades")
        )
        
        # Empresa Flags 
        empresa_flags = (planilla.payload_inicial or {}).get("empresa", {}).get("flags", {}) or {}
        empresa_exonerada = bool(empresa_flags.get("empresa_exonerada", False))

        # --- Mapa de flags por empleado (desde payload_inicial) ---
        payload_inicial = planilla.payload_inicial or {}
        empleados_payload = payload_inicial.get("empleados", []) or []

        flags_map = {}
        for e in empleados_payload:
            tipo_doc = e.get("tipo_doc") or ""
            numero_doc = e.get("numero_doc") or e.get("num_doc") or ""
            f = (e.get("flags") or {})
            flags_map[(tipo_doc, numero_doc)] = {
                "aplica_salud": bool(f.get("aplica_salud", True)),
                "aplica_pension": bool(f.get("aplica_pension", True)),
                "aplica_arl": bool(f.get("aplica_arl", True)),
                "aplica_caja": bool(f.get("aplica_caja", True)),
            }

        empleados_ok = 0
        empleados_error = 0
        warnings = 0

        tot_emp = D0
        tot_empl = D0

        tot_salud_emp = D0
        tot_salud_empl = D0
        tot_pension_emp = D0
        tot_pension_empl = D0
        tot_arl_empl = D0
        tot_caja_empl = D0

        for d in detalles:
            errores = []

            dias = int(d.dias_cotizados or 0)
            ibc_base = _to_decimal(d.ibc)

            # --- reglas mínimas por novedades (ING/RET override días) ---
            for n in d.novedades.all():
                cod = (n.tipo_novedad or "").upper()
                if cod in ("RET", "ING"):
                    dias_override = (n.metadata or {}).get("dias_cotizados")
                    if dias_override is not None:
                        try:
                            dias = int(dias_override)
                        except ValueError:
                            errores.append(f"{cod}: dias_cotizados inválido")

            # --- validaciones mínimas ---
            if dias < 0 or dias > 30:
                errores.append("dias_cotizados fuera de rango (0..30)")
            if ibc_base < 0:
                errores.append("ibc negativo")

            # IBC base por defecto (si no cotiza días, IBC=0)
            ibc_subs = D0 if dias == 0 else ibc_base

            # asignación inicial
            d.dias_cotizados = dias
            d.ibc_salud = ibc_subs
            d.ibc_pension = ibc_subs
            d.ibc_arl = ibc_subs

            # --- A.2: mínimo proporcional por subsistema + tope ---
            dias_salud = _to_decimal(getattr(d, "dias_salud", dias))
            dias_pension = _to_decimal(getattr(d, "dias_pension", dias))
            dias_arl = _to_decimal(getattr(d, "dias_arl", dias))

            ibc_min_salud = _q2(smmlv * dias_salud / dias_base) if dias_salud > 0 else D0
            ibc_min_pension = _q2(smmlv * dias_pension / dias_base) if dias_pension > 0 else D0
            ibc_min_arl = _q2(smmlv * dias_arl / dias_base) if dias_arl > 0 else D0

            d.ibc_salud = _clamp(_to_decimal(d.ibc_salud), ibc_min_salud, ibc_max_global)
            d.ibc_pension = _clamp(_to_decimal(d.ibc_pension), ibc_min_pension, ibc_max_global)
            d.ibc_arl = _clamp(_to_decimal(d.ibc_arl), ibc_min_arl, ibc_max_global)

            # --- Flags por subsistema ---
            f = flags_map.get(
                (d.tipo_doc, d.numero_doc),
                {"aplica_salud": True, "aplica_pension": True, "aplica_arl": True, "aplica_caja": True},
            )
            aplica_salud = f["aplica_salud"]
            aplica_pension = f["aplica_pension"]
            aplica_arl = f["aplica_arl"]
            aplica_caja = f["aplica_caja"]
            
            # --- Ajustes según tipo y subtipo de cotizante ---
            # Si tipo_cotizante == "23": solo ARL (sin pensión, salud ni CCF)
            if d.tipo_cotizante == "23":
                aplica_salud = False
                aplica_pension = False
                aplica_caja = False
                # Mantener aplica_arl = True (solo ARL)
                # Establecer días en 0 para subsistemas que no aplican
                d.dias_salud = 0
                d.dias_pension = 0
                d.dias_caja = 0
                # Establecer IBCs en 0 para subsistemas que no aplican
                d.ibc_salud = D0
                d.ibc_pension = D0
            
            # Si subtipo_cotizante == "1": pensionado activo, no liquidación de pensiones AFP
            if d.subtipo_cotizante == "1":
                aplica_pension = False
                d.dias_pension = 0
                d.ibc_pension = D0

            # Solo no aplica pensión cuando subtipo tiene valor y es distinto de "12". Si está en blanco/0/00 o es "12", sí aplica.
            subtipo_norm = str(d.subtipo_cotizante or "").strip().zfill(2)
            if subtipo_norm not in ("00", "12"):
                aplica_pension = False
                d.dias_pension = 0
                d.ibc_pension = D0

            aportes = {}
            aportes_emp = D0
            aportes_empl = D0

            # --- Exoneración (empresa_exonerada AND <10 SMMLV AND NO integral) ---
            emp_payload = next(
                (
                    e for e in empleados_payload
                    if (e.get("tipo_doc") or "") == d.tipo_doc
                    and (e.get("numero_doc") or e.get("num_doc") or "") == d.numero_doc
                ),
                {},
            )

            emp_flags = (emp_payload.get("flags") or {})
            salario_integral = bool(emp_flags.get("salario_integral", False))

            # usa el salario_basico del payload (Nomiweb lo manda)
            salario_basico = _to_decimal(emp_payload.get("salario_basico"))

            smmlv_mayor_10 = salario_basico >= (smmlv * Decimal("10"))

            aplica_exoneracion = (
                empresa_exonerada
                and (not salario_integral)
                and (not smmlv_mayor_10)
            )
            
            if not errores:
                # IBC efectivos según flags
                ibc_salud_calc = _to_decimal(d.ibc_salud) if aplica_salud else D0
                ibc_pension_calc = _to_decimal(d.ibc_pension) if aplica_pension else D0
                ibc_arl_calc = _to_decimal(d.ibc_arl) if aplica_arl else D0

                # Salud: cuando IBC > 10 SMLV usar tasas de conceptosfijos (idfijo 8 y 18) = 4% + 8.5% = 12.5%
                # Los integrales siempre superan 10 SMLV (mínimo ~25 SMLV, IBC ~70% ≈ 17.5 SMLV)
                ibc_mayor_10_smmlv = ibc_salud_calc > (smmlv * Decimal("10")) or salario_integral
                if aplica_salud:
                    salud_emp = _calc_pct(ibc_salud_calc, tasa_salud_emp_param)
                    if ibc_mayor_10_smmlv:
                        salud_empl = _calc_pct(ibc_salud_calc, tasa_salud_empl_ibc10_param)
                    elif aplica_exoneracion:
                        salud_empl = D0
                    else:
                        salud_empl = _calc_pct(ibc_salud_calc, TASA_SALUD_EMPL)
                else:
                    salud_emp = salud_empl = D0

                pension_emp = _calc_pct(ibc_pension_calc, TASA_PENSION_EMP) if aplica_pension else D0
                pension_empl = _calc_pct(ibc_pension_calc, TASA_PENSION_EMPL) if aplica_pension else D0

                # ARL
                # VAC/IGE/LMA: mismos días e IBC que salud, pero tarifa 0% (no exposición a riesgos)
                tiene_novedad_sin_riesgo = any(
                    (n.tipo_novedad or "").upper() in ("VAC", "IGE", "LMA")
                    for n in d.novedades.all()
                )
                if aplica_arl and not tiene_novedad_sin_riesgo:
                    arl_pct = ARL_TASAS.get(str(d.riesgo_arl))
                    if not arl_pct:
                        errores.append("riesgo_arl inválido (1..5)")
                        arl_empl = D0
                    else:
                        arl_empl = _calc_pct(ibc_arl_calc, arl_pct)
                else:
                    arl_empl = D0

                # Caja
                caja_empl = _calc_pct(ibc_salud_calc, TASA_CAJA) if (aplica_caja and d.caja_compensacion) else D0
                if aplica_exoneracion:
                    caja_empl = D0

                # FSP (Fondo Solidaridad Pensional) - solo si aplica pensión
                # Se calcula sobre el IBC de pensión antes de redondear
                fsp_solidaridad = D0
                fsp_subsistencia = D0
                if aplica_pension and fsp_porcentajes:
                    fsp_solidaridad, fsp_subsistencia = _calcular_fsp(
                        ibc_pension_calc, smmlv, fsp_porcentajes
                    )

                # Aplicar redondeo de cotizaciones según Decreto 1990 de 2016
                # Las cotizaciones se redondean al múltiplo de 100 superior.
                # Importante: salud y pensión se redondean como TOTAL (campo 47/55),
                # no cada componente por separado, para evitar Error 191.
                salud_total = salud_emp + salud_empl
                pension_total = pension_emp + pension_empl
                salud_total_redondeado = redondear_cotizacion(salud_total)
                pension_total_redondeado = redondear_cotizacion(pension_total)
                arl_empl_redondeado = redondear_cotizacion(arl_empl)
                caja_empl_redondeado = redondear_cotizacion(caja_empl)

                # Repartir proporcionalmente para aportes empleado/empleador (4% emp, 12% empl)
                if pension_total > 0:
                    pension_emp_redondeado = int(round(pension_total_redondeado * float(TASA_PENSION_EMP) / float(TASA_PENSION_EMP + TASA_PENSION_EMPL)))
                    pension_empl_redondeado = pension_total_redondeado - pension_emp_redondeado
                else:
                    pension_emp_redondeado = pension_empl_redondeado = 0

                if salud_total > 0:
                    if salud_empl == 0:
                        salud_emp_redondeado = salud_total_redondeado
                        salud_empl_redondeado = 0
                    else:
                        salud_emp_redondeado = int(round(salud_total_redondeado * float(TASA_SALUD_EMP) / float(TASA_SALUD_EMP + TASA_SALUD_EMPL)))
                        salud_empl_redondeado = salud_total_redondeado - salud_emp_redondeado
                else:
                    salud_emp_redondeado = salud_empl_redondeado = 0

                aportes = {
                    "salud": {
                        "aplica": aplica_salud,
                        "ibc": str(_q2(ibc_salud_calc)),
                        "empleado": str(salud_emp_redondeado),
                        "empleador": str(salud_empl_redondeado),
                        "total": str(salud_total_redondeado),
                        "exonerado_empleador": aplica_exoneracion,
                    },
                    "pension": {
                        "aplica": aplica_pension,
                        "ibc": str(_q2(ibc_pension_calc)),
                        "empleado": str(pension_emp_redondeado),
                        "empleador": str(pension_empl_redondeado),
                        "total": str(pension_total_redondeado),
                        "fsp_solidaridad": str(fsp_solidaridad),
                        "fsp_subsistencia": str(fsp_subsistencia),
                    },
                    "arl": {
                        "aplica": aplica_arl,
                        "ibc": str(_q2(ibc_arl_calc)),
                        "riesgo": str(d.riesgo_arl),
                        "empleador": str(arl_empl_redondeado),
                    },
                    "caja": {
                        "aplica": aplica_caja and bool(d.caja_compensacion),
                        "ibc": str(_q2(ibc_salud_calc)),
                        "empleador": str(caja_empl_redondeado),
                        "exonerado": aplica_exoneracion,
                    },
                }

                # Usar valores redondeados para los totales
                aportes_emp = Decimal(salud_emp_redondeado + pension_emp_redondeado)
                aportes_empl = Decimal(salud_empl_redondeado + pension_empl_redondeado + arl_empl_redondeado + caja_empl_redondeado)

            # persistencia
            if errores:
                d.estado = "CON_ERROR"
                d.errores = errores
                d.aportes = {}
                d.aportes_empleado = D0
                d.aportes_empleador = D0
                empleados_error += 1
            else:
                d.estado = "OK"
                d.errores = []
                d.aportes = aportes
                d.aportes_empleado = aportes_emp
                d.aportes_empleador = aportes_empl
                empleados_ok += 1

                tot_emp += aportes_emp
                tot_empl += aportes_empl

                tot_salud_emp += Decimal(aportes["salud"]["empleado"])
                tot_salud_empl += Decimal(aportes["salud"]["empleador"])
                tot_pension_emp += Decimal(aportes["pension"]["empleado"])
                tot_pension_empl += Decimal(aportes["pension"]["empleador"])
                tot_arl_empl += Decimal(aportes["arl"]["empleador"])
                tot_caja_empl += Decimal(aportes["caja"]["empleador"])

            d.save(update_fields=[
                "dias_cotizados",
                "dias_salud", "dias_pension", "dias_arl", "dias_caja",
                "ibc_salud", "ibc_pension", "ibc_arl",
                "estado", "errores",
                "aportes", "aportes_empleado", "aportes_empleador",
            ])

        planilla.resumen = {
            "empleados_procesados": empleados_ok + empleados_error,
            "empleados_con_error": empleados_error,
            "warnings": warnings,
        }

        planilla.totales = {
            "empleado": str(_q2(tot_emp)),
            "empleador": str(_q2(tot_empl)),
            "total": str(_q2(tot_emp + tot_empl)),
            "subsistemas": {
                "salud": {
                    "empleado": str(_q2(tot_salud_emp)),
                    "empleador": str(_q2(tot_salud_empl)),
                    "total": str(_q2(tot_salud_emp + tot_salud_empl)),
                },
                "pension": {
                    "empleado": str(_q2(tot_pension_emp)),
                    "empleador": str(_q2(tot_pension_empl)),
                    "total": str(_q2(tot_pension_emp + tot_pension_empl)),
                },
                "arl": {"empleador": str(_q2(tot_arl_empl))},
                "caja": {"empleador": str(_q2(tot_caja_empl))},
            }
        }

        planilla.estado = "COMPLETADA" if empleados_error == 0 else "CON_ERRORES"
        planilla.save(update_fields=["resumen", "totales", "estado"])

        return {
            "resumen": planilla.resumen,
            "totales": planilla.totales,
            "estado": planilla.estado,
        }