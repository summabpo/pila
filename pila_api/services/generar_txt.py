# pila_api/services/generar_txt.py

from decimal import Decimal
from django.db import transaction
from pila_api.models import PilaPlanilla, PilaPlanillaDetalle
from pila_api.renderers.fixed_width.registro_01 import Registro01Renderer
from pila_api.renderers.fixed_width.registro_02 import Registro02Renderer
from pila_api.utils.redondeos import redondear_cotizacion


def _format_tarifa_arl(tarifa):
    """
    Formatea la tarifa ARL para el campo 61 (381-389).
    
    La tarifa viene del payload desde centrotrabajo.tarifaarl en formato porcentaje.
    Ejemplos: "0.522" (0.522%), "4.350" (4.350%), "6.960" (6.960%)
    Debe convertirse a formato decimal PILA dividiendo por 100.
    
    Formato PILA: 9 caracteres (decimal con 7 decimales)
    Ejemplo: 0.522 (porcentaje) -> 0.00522 -> "0.0052200" (9 chars)
    Ejemplo: 4.350 (porcentaje) -> 0.04350 -> "0.0435000" (9 chars)
    Ejemplo: 6.960 (porcentaje) -> 0.06960 -> "0.0696000" (9 chars)
    """
    if tarifa is None:
        return ""
    
    try:
        # Convertir a Decimal para precisión
        if isinstance(tarifa, str):
            tarifa = Decimal(tarifa)
        elif not isinstance(tarifa, Decimal):
            tarifa = Decimal(str(tarifa))
        
        # La tarifa siempre viene como porcentaje desde centrotrabajo.tarifaarl
        # Dividir por 100 para convertir a decimal (0.522% -> 0.00522)
        tarifa_decimal = tarifa / Decimal("100")
        
        # Formatear con 7 decimales (total 9 caracteres incluyendo punto y 1 dígito entero)
        tarifa_formateada = f"{tarifa_decimal:.7f}"
        
        # Asegurar que tenga exactamente 9 caracteres
        if len(tarifa_formateada) != 9:
            # Si tiene menos de 9, rellenar con ceros a la derecha
            tarifa_formateada = tarifa_formateada.ljust(9, '0')
        elif len(tarifa_formateada) > 9:
            # Si tiene más de 9, truncar
            tarifa_formateada = tarifa_formateada[:9]
        
        return tarifa_formateada
    except:
        return ""


# Mapeo clase_riesgo (1-5) -> tarifa ARL en % (para fallback cuando falta en payload)
_CLASE_RIESGO_A_TARIFA = {"1": "0.522", "2": "1.044", "3": "2.436", "4": "4.350", "5": "6.960"}


def generar_txt_planilla(planilla_id: int, filtro_tipo_planilla: str | None = None) -> str:
    """
    Genera el archivo TXT PILA completo para una planilla.
    
    Estructura:
    - 1 línea registro tipo 01 (encabezado)
    - N líneas registro tipo 02 (una por cada detalle/empleado)
    
    Args:
        planilla_id: ID de la planilla a generar
        filtro_tipo_planilla: Si "K" solo empleados tipo 23 (estudiantes).
            Si "E" solo empleados tipo != 23. Si None, todos.
        
    Returns:
        String con el contenido del archivo TXT (líneas separadas por \\n)
        
    Raises:
        PilaPlanilla.DoesNotExist: Si la planilla no existe
        ValueError: Si faltan datos requeridos en el payload
    """
    with transaction.atomic():
        # Cargar planilla con detalles
        planilla = PilaPlanilla.objects.select_for_update().get(planilla_id=planilla_id)
        detalles = list(
            PilaPlanillaDetalle.objects
            .filter(planilla=planilla, estado="OK")
            .order_by("id")
        )
        
        # Filtrar por tipo de planilla: K (solo estudiantes 23) o E (solo no estudiantes)
        if filtro_tipo_planilla == "K":
            detalles = [d for d in detalles if d.tipo_cotizante == "23"]
        elif filtro_tipo_planilla == "E":
            detalles = [d for d in detalles if d.tipo_cotizante != "23"]
        
        if not detalles:
            raise ValueError(
                f"La planilla {planilla_id} no tiene detalles válidos"
                + (f" para tipo planilla {filtro_tipo_planilla}" if filtro_tipo_planilla else "")
            )
        
        payload = planilla.payload_inicial or {}
        
        # Extraer datos de empresa
        empresa = payload.get("empresa", {})
        if not empresa:
            raise ValueError("Falta 'empresa' en payload_inicial")
        
        planilla_data = payload.get("planilla", {})
        
        # ============================================
        # REGISTRO 01 (Encabezado)
        # ============================================
        
        # Total cotizantes = afiliados ÚNICOS (tipo_doc + numero_doc). No contar líneas:
        # un empleado con VAC + NORMAL tiene 2 líneas tipo 02 pero es 1 cotizante (Error 184).
        cotizantes_unicos = set((d.tipo_doc, d.numero_doc) for d in detalles)
        total_cotizantes = len(cotizantes_unicos)
        valor_total_nomina = 0
        for detalle in detalles:
            aportes_detalle = detalle.aportes or {}
            caja_detalle = aportes_detalle.get("caja", {})
            ibc_caja = caja_detalle.get("ibc", 0)
            valor_total_nomina += int(float(ibc_caja))
        
        # El NIT en el registro 01 (pos 210-218) es de 9 caracteres, sin DV
        nit_empresa = str(empresa.get("nit", "")).strip()
        # Si el NIT incluye el DV concatenado, tomar solo los primeros 9 dígitos
        if len(nit_empresa) > 9:
            nit_empresa = nit_empresa[:9]
        
        # Dígito de verificación (separado del NIT)
        dv_empresa = str(empresa.get("dv", "")).strip()
        
        # Tipo de presentación (U=única, S=sucursal)
        tipo_presentacion = str(empresa.get("tipo_presentacion_planilla", "U")).strip()
        
        # Código ARL del aportante (6 caracteres)
        codigo_arl_aportante = str(empresa.get("codigo_arl", "")).strip()
        
        # Periodo cotización (pos 305-311): mes que se liquida. Periodo pago (pos 312-318): mes siguiente
        periodo_cotizacion = planilla.periodo  # YYYY-MM del mes liquidado
        año, mes = int(periodo_cotizacion[:4]), int(periodo_cotizacion[5:7])
        mes_siguiente = mes + 1 if mes < 12 else 1
        año_siguiente = año if mes < 12 else año + 1
        periodo_pago = f"{año_siguiente}-{mes_siguiente:02d}"  # Un mes adicional (ej: 2025-12 → 2026-01)
        
        # Tipo planilla: K para estudiantes (tipo 23), E para resto
        if filtro_tipo_planilla:
            tipo_planilla_01 = filtro_tipo_planilla
        else:
            tipo_planilla_01 = planilla_data.get("tipo_planilla", "E")
        
        data_01 = {
            "codigo_3_7": "10001",  # TODO: determinar si viene del payload o es fijo
            "razon_social": empresa.get("razon_social", ""),
            "tipo_doc": "NI",  # NIT (estándar para empresas)
            "num_doc": nit_empresa,
            "dv": dv_empresa,  # Campo 9 (pos 226): Dígito de verificación
            "tipo_planilla": tipo_planilla_01,
            "forma_presentacion": tipo_presentacion,  # Campo 10 (pos 248): U=única, S=sucursal
            "codigo_arl": codigo_arl_aportante,  # Campo 18 (pos 299-304): Código ARL del aportante
            "periodo_cotizacion": periodo_cotizacion,  # Pos 305-311: mes de aportes liquidados
            "periodo_pago": periodo_pago,  # Pos 312-318: mes siguiente al liquidado
            "total_cotizantes": total_cotizantes,  # Campo 19 (pos 339-343)
            "valor_total_nomina": valor_total_nomina,  # Campo 20 (pos 344-355)
            "tipo_aportante": "01",  # Campo 30 (pos 356-357): 01 = empleador
        }
        
        renderer_01 = Registro01Renderer()
        linea_01 = renderer_01.render(data_01)
        
        # ============================================
        # REGISTROS 02 (Detalles por empleado)
        # ============================================
        
        lineas_02 = []
        renderer_02 = Registro02Renderer()
        
        # Construir mapa de empleados del payload para acceso rápido
        empleados_payload = payload.get("empleados", [])
        empleados_map = {}
        for emp in empleados_payload:
            key = (emp.get("tipo_doc", ""), emp.get("num_doc", "") or emp.get("numero_doc", ""))
            empleados_map[key] = emp
        
        secuencia_global = 1
        for detalle in detalles:
            secuencia = f"{secuencia_global:05d}"  # 00001, 00002, ...
            secuencia_global += 1
            
            # Buscar datos adicionales del empleado en el payload
            emp_payload = empleados_map.get((detalle.tipo_doc, detalle.numero_doc), {})
            
            # Extraer entidades
            entidades = emp_payload.get("entidades", {})
            
            # Extraer códigos DANE
            cod_departamento = emp_payload.get("cod_departamento", "")
            cod_municipio = emp_payload.get("cod_municipio", "")
            municipio_concat = f"{cod_departamento}{cod_municipio}".ljust(5)[:5]
            
            # Extraer nombres completos (4 campos)
            primer_apellido = emp_payload.get("primer_apellido", detalle.primer_apellido)
            segundo_apellido = emp_payload.get("segundo_apellido", "")
            primer_nombre = emp_payload.get("primer_nombre", detalle.primer_nombre)
            segundo_nombre = emp_payload.get("segundo_nombre", "")
            
            # Extraer días por subsistema desde el detalle
            dias_salud = detalle.dias_salud
            dias_pension = detalle.dias_pension
            dias_arl = detalle.dias_arl
            dias_caja = detalle.dias_caja
            
            # Extraer IBCs y aportes desde el JSON calculado
            aportes = detalle.aportes or {}
            
            salud = aportes.get("salud", {})
            pension = aportes.get("pension", {})
            arl = aportes.get("arl", {})
            caja = aportes.get("caja", {})
            
            # Salario básico
            salario_basico = emp_payload.get("salario_basico", 0)
            
            # Determinar tipo de salario (Campo 41: X=integral, F=fijo, V=variable)
            flags = emp_payload.get("flags", {})
            if flags.get("salario_integral", False):
                tipo_salario = "X"  # Integral
            else:
                tipo_salario = "F"
            
            # Extraer tarifas (incluyendo tarifa ARL)
            tarifas = emp_payload.get("tarifas", {})
            tarifa_arl = tarifas.get("arl")
            
            # Centro de trabajo (campo 62, pos 390-398): código según tarifa ARL
            centro_trabajo = emp_payload.get("codigo_centro_trabajo", emp_payload.get("centro_trabajo", 0))
            
            # ============================================
            # NOVEDADES: Extraer desde PilaNovedad
            # ============================================
            novedades_detalle = detalle.novedades.all()
            
            # Campos de novedades (posiciones 137-149)
            nov_ing = ""  # Campo 15 (pos 137)
            nov_ret = ""  # Campo 16 (pos 138)
            nov_vsp = ""  # Campo 21 (pos 143)
            nov_vst = ""  # Campo 23 (pos 145)
            nov_sln = ""  # Campo 24 (pos 146)
            nov_ige = ""  # Campo 25 (pos 147)
            nov_lma = ""  # Campo 26 (pos 148)
            nov_vac = ""  # Campo 27 (pos 149)
            irl_dias = 0  # Campo 30 (pos 152-153)
            
            # Fechas de novedades (campos 80-94)
            fecha_ing = ""  # Campo 80 (pos 515-524)
            fecha_ret = ""  # Campo 81 (pos 525-534)
            fecha_vsp_inicio = ""  # Campo 82 (pos 535-544)
            fecha_sln_inicio = ""  # Campo 83 (pos 545-554)
            fecha_sln_fin = ""  # Campo 84 (pos 555-564)
            fecha_ige_inicio = ""  # Campo 85 (pos 565-574)
            fecha_ige_fin = ""  # Campo 86 (pos 575-584)
            fecha_lma_inicio = ""  # Campo 87 (pos 585-594)
            fecha_lma_fin = ""  # Campo 88 (pos 595-604)
            fecha_vac_inicio = ""  # Campo 89 (pos 605-614)
            fecha_vac_fin = ""  # Campo 90 (pos 615-624)
            fecha_irl_inicio = ""  # Campo 93 (pos 645-654)
            fecha_irl_fin = ""  # Campo 94 (pos 655-664)
            
            for nov in novedades_detalle:
                codigo = nov.tipo_novedad.upper()
                
                if codigo == "ING":
                    nov_ing = "X"
                    fecha_ing = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                elif codigo == "RET":
                    nov_ret = "X"
                    fecha_ret = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                elif codigo == "VSP":
                    nov_vsp = "X"
                    fecha_vsp_inicio = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                elif codigo == "VST":
                    nov_vst = "X"
                elif codigo == "SLN":
                    nov_sln = "X"
                    fecha_sln_inicio = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                    fecha_sln_fin = nov.fecha_fin.isoformat() if nov.fecha_fin else ""
                elif codigo == "IGE":
                    nov_ige = "X"
                    fecha_ige_inicio = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                    fecha_ige_fin = nov.fecha_fin.isoformat() if nov.fecha_fin else ""
                elif codigo == "LMA":
                    nov_lma = "X"
                    fecha_lma_inicio = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                    fecha_lma_fin = nov.fecha_fin.isoformat() if nov.fecha_fin else ""
                elif codigo == "VAC":
                    nov_vac = "X"
                    fecha_vac_inicio = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                    fecha_vac_fin = nov.fecha_fin.isoformat() if nov.fecha_fin else ""
                elif codigo == "IRL":
                    irl_dias = nov.dias or 0
                    fecha_irl_inicio = nov.fecha_inicio.isoformat() if nov.fecha_inicio else ""
                    fecha_irl_fin = nov.fecha_fin.isoformat() if nov.fecha_fin else ""
            
            # Calcular parafiscales con redondeo según Decreto 1990
            ibc_caja_valor = float(caja.get("ibc", 0))
            if caja.get("aplica", False) and ibc_caja_valor > 0:
                valor_ccf_calc = ibc_caja_valor * 0.04
                valor_sena_calc = ibc_caja_valor * 0.02 if not caja.get("exonerado", False) else 0
                valor_icbf_calc = ibc_caja_valor * 0.03 if not caja.get("exonerado", False) else 0
                
                tarifa_ccf_val = "0.04000"
                valor_ccf_val = redondear_cotizacion(valor_ccf_calc)
                tarifa_sena_val = "0.02000" if not caja.get("exonerado", False) else ""
                valor_sena_val = redondear_cotizacion(valor_sena_calc) if not caja.get("exonerado", False) else 0
                tarifa_icbf_val = "0.03000" if not caja.get("exonerado", False) else ""
                valor_icbf_val = redondear_cotizacion(valor_icbf_calc) if not caja.get("exonerado", False) else 0
            else:
                tarifa_ccf_val = ""
                valor_ccf_val = 0
                tarifa_sena_val = ""
                valor_sena_val = 0
                tarifa_icbf_val = ""
                valor_icbf_val = 0
            
            # No obligado a pensiones: tipo 23, o subtipo con valor distinto de 12 (si blanco/0/00 o 12 sí obligado)
            subtipo_norm = str(detalle.subtipo_cotizante or "").strip().zfill(2)
            no_obligado_pension = detalle.tipo_cotizante == "23" or subtipo_norm not in ("00", "12")
            
            # Error 835: Si hay novedades de ausentismo (VAC, IGE, LMA, SLN, IRL), tarifa ARL debe ser 0
            # IRL = incapacidad riesgo laboral: días sin exposición a riesgos, tarifa 0 en esa línea
            # Pensionados/exonerados de pensión SÍ cotizan ARL: mantienen su tarifa real (no 0)
            tiene_novedad_ausentismo = bool(nov_vac or nov_ige or nov_lma or nov_sln or irl_dias)
            if tiene_novedad_ausentismo:
                tarifa_arl_formateada = "0.0000000"
            else:
                # Pensionados: priorizar clase_riesgo (Error 355 exige 0.0435 según clase)
                # El payload a veces trae tarifa 0/vacía para exonerados; clase_riesgo es fiable
                clase_riesgo = str(emp_payload.get("clase_riesgo") or detalle.riesgo_arl or "").strip()
                tarifa_arl_efectiva = _CLASE_RIESGO_A_TARIFA.get(clase_riesgo) if no_obligado_pension else None
                if not tarifa_arl_efectiva:
                    tarifa_arl_efectiva = tarifa_arl
                if not tarifa_arl_efectiva or (isinstance(tarifa_arl_efectiva, (int, float)) and float(tarifa_arl_efectiva) == 0):
                    tarifa_arl_efectiva = _CLASE_RIESGO_A_TARIFA.get(clase_riesgo)
                tarifa_arl_formateada = _format_tarifa_arl(tarifa_arl_efectiva) if tarifa_arl_efectiva else ""

            # Construir data para Registro02Renderer
            data_02 = {
                "secuencia": secuencia,
                "tipo_doc": detalle.tipo_doc,
                "num_doc": detalle.numero_doc,
                "tipo_cotizante": detalle.tipo_cotizante,
                "subtipo_cotizante": detalle.subtipo_cotizante or "00",
                
                # DANE
                "municipio": municipio_concat,
                
                # Nombres completos (4 campos)
                "papellido": primer_apellido,
                "sapellido": segundo_apellido,
                "pnombre": primer_nombre,
                "snombre": segundo_nombre,
                
                # Novedades (campos 15-30: posiciones 137-153)
                "nov_ing": nov_ing,  # Campo 15 (pos 137)
                "nov_ret": nov_ret,  # Campo 16 (pos 138)
                "nov_vsp": nov_vsp,  # Campo 21 (pos 143)
                "nov_vst": nov_vst,  # Campo 23 (pos 145)
                "nov_sln": nov_sln,  # Campo 24 (pos 146)
                "nov_ige": nov_ige,  # Campo 25 (pos 147)
                "nov_lma": nov_lma,  # Campo 26 (pos 148)
                "nov_vac": nov_vac,  # Campo 27 (pos 149)
                "irl_dias": irl_dias,  # Campo 30 (pos 152-153)
                
                # Entidades (códigos de 6 caracteres)
                # Campo 31 (154-159): AFP en blanco si no obligado a pensiones (tipo 23 o subtipo != 12)
                # Evitar None/str(None) para Aportes en Línea
                "afp": "" if no_obligado_pension else (entidades.get("afp") or ""),
                # Errores 242/245: EPS y CCF vacíos para tipo 23 (no aporta salud ni CCF)
                "eps": "" if detalle.tipo_cotizante == "23" else entidades.get("eps", ""),  # Campo 33 (166-171)
                "ccf": "" if detalle.tipo_cotizante == "23" else entidades.get("caja", ""),  # Campo 35 (178-183)
                
                # Días por subsistema (184-191)
                "dias_salud": int(dias_salud),
                "dias_pension": int(dias_pension),
                "dias_arl": int(dias_arl),
                "dias_caja": int(dias_caja),
                
                # Campos 192-332 (IBCs y valores calculados)
                "v_192_200": int(float(salario_basico)),  # Campo 40: Salario básico (192-200)
                # Error 466: Tipo salario vacío para tipo 23 (no aplica F/X/V)
                "tipo_salario": "" if detalle.tipo_cotizante == "23" else tipo_salario,  # Campo 41 (201)
                "ibc_pension": int(float(pension.get("ibc", 0))),  # Campo 42: IBC pensión (202-210)
                "v_210_218": int(float(salud.get("ibc", 0))),  # Campo 43: IBC salud (211-219)
                "v_219_227": int(float(arl.get("ibc", 0))),  # Campo 44: IBC ARL (220-228)
                "v_228_236": int(float(caja.get("ibc", 0))),  # Campo 45: IBC CCF (229-237)
                
                # Tarifas y cotizaciones
                # Tarifa pensión 0 si no obligado a pensiones (tipo 23 o subtipo != 12)
                "v_237_245": "0.00000" if no_obligado_pension else "0.16000",  # Campo 46 (238-244)
                "v_246_254": int(float(pension.get("total", 0))),  # Campo 47: Cotización pensión
                
                # Campos adicionales
                "v_255_263": 0,  # Campo 48: Aporte voluntario afiliado
                "v_264_272": 0,  # Campo 49: Aporte voluntario aportante
                "v_273_281": 0,  # Campo 50: Total cotización pensión
                "v_282_290": int(float(pension.get("fsp_solidaridad", 0))),  # Campo 51: Fondo solidaridad (FSP)
                "v_291_299": int(float(pension.get("fsp_subsistencia", 0))),  # Campo 52: Fondo subsistencia (FSP)
                "v_300_308": 0,  # Campo 53: Valor no retenido
                
                # Salud
                # Error 360: Tarifa salud 0 para cotizantes no obligados a EPS (tipo 23)
                # IBC > 10 SMLV: 12.5% (conceptosfijos idfijo 8+18). Exonerado: 4% empleado.
                "v_309_317": (
                    "0.00000" if detalle.tipo_cotizante == "23"
                    else ("0.12500" if float(salud.get("empleador", 0) or 0) > 0 else "0.04000")
                ),  # Campo 54 (308-314)
                "v_318_326": int(float(salud.get("total", 0))),  # Campo 55: Cotización salud
                "v_327_332": 0,  # Campo 56: UPC adicional
                
                # ARL
                # Error 194: Cotización obligatoria riesgos debe ser $0 cuando hay ausentismo (IRL, VAC, etc.)
                "tarifa_arl": tarifa_arl_formateada,
                "centro_trabajo": centro_trabajo,
                "cotizacion_arl": 0 if tiene_novedad_ausentismo else arl.get("empleador", 0),
                
                # Parafiscales (valores ya calculados con redondeo)
                "tarifa_ccf": tarifa_ccf_val,
                "valor_ccf": valor_ccf_val,
                "tarifa_sena": tarifa_sena_val,
                "valor_sena": valor_sena_val,
                "tarifa_icbf": tarifa_icbf_val,
                "valor_icbf": valor_icbf_val,
                
                # Error 610: Tipo 23 no aplica exoneración; valor esperado N
                "exonerado": "N" if detalle.tipo_cotizante == "23" else (
                    "S" if (caja.get("exonerado", False) or salud.get("exonerado_empleador", False)) else "N"
                ),
                "codigo_arl": entidades.get("arl", ""),
                "clase_riesgo": str(detalle.riesgo_arl) if detalle.riesgo_arl else "",
                "horas_laboradas": int(dias_caja) * 8 if dias_caja > 0 else 0,
                # Campo 95 (pos 665-673): IBC otros parafiscales (SENA/ICBF). Obligatorio cuando hay aporte.
                # Error 816: no puede ser 0 cuando hay aporte obligatorio y 30 días cotizados
                "ibc_otros_parafiscales": int(ibc_caja_valor) if (valor_sena_val or valor_icbf_val) else 0,
                "actividad_economica_arl": emp_payload.get("actividad_economica_arl", ""),
                
                # Fechas de novedades (campos 80-94)
                "fecha_ing": fecha_ing,
                "fecha_ret": fecha_ret,
                "fecha_vsp_inicio": fecha_vsp_inicio,
                "fecha_sln_inicio": fecha_sln_inicio,
                "fecha_sln_fin": fecha_sln_fin,
                "fecha_ige_inicio": fecha_ige_inicio,
                "fecha_ige_fin": fecha_ige_fin,
                "fecha_lma_inicio": fecha_lma_inicio,
                "fecha_lma_fin": fecha_lma_fin,
                "fecha_vac_inicio": fecha_vac_inicio,
                "fecha_vac_fin": fecha_vac_fin,
                "fecha_irl_inicio": fecha_irl_inicio,
                "fecha_irl_fin": fecha_irl_fin,
                
                # Campos 333-693: resto sin mapear aún
                "raw_333_693": None,
            }
            
            linea_02 = renderer_02.render(data_02)
            
            # Validar longitud y truncar si es necesario
            if len(linea_02) == 694:
                linea_02 = linea_02[:693]
            elif len(linea_02) != 693:
                raise ValueError(f"Línea {secuencia_global-1} tiene {len(linea_02)} caracteres, esperado 693")
            
            lineas_02.append(linea_02)
        
        # ============================================
        # ENSAMBLAR ARCHIVO COMPLETO
        # ============================================
        
        # Validar y corregir longitudes antes de ensamblar
        lineas_corregidas = []
        
        # Validar línea 01
        if len(linea_01) != 359:
            if len(linea_01) > 359:
                linea_01 = linea_01[:359]
            else:
                raise ValueError(f"Registro 01 tiene {len(linea_01)} caracteres, esperado 359")
        lineas_corregidas.append(linea_01)
        
        # Validar y corregir líneas 02
        for i, linea in enumerate(lineas_02, start=1):
            # Asegurar que la línea tenga exactamente 693 caracteres
            if len(linea) < 693:
                # Rellenar con espacios al final
                linea = linea.ljust(693, ' ')
            elif len(linea) > 693:
                # Truncar
                linea = linea[:693]
            
            lineas_corregidas.append(linea)
        
        contenido_txt = "\n".join(lineas_corregidas)
        
        # Opcional: marcar que el archivo fue generado
        planilla.tiene_archivo = True
        planilla.save(update_fields=["tiene_archivo"])
        
        return contenido_txt
