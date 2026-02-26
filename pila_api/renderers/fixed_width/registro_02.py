# pila_api/renderers/fixed_width/registro_02.py

from pila_api.renderers.fixed_width.base import FixedWidthLine


class Registro02Renderer:
    """
    Registro tipo 02 - Detalle cotizante (ancho fijo)
    Basado en ATI_COL28736 (2).TXT
    Longitud observada en el ejemplo: 693
    """
    LEN = 693

    def render(self, data: dict) -> str:
        l = FixedWidthLine(self.LEN)

        # 1-2 tipo registro
        l.set_alpha(1, 2, "02")

        # 3-7 secuencia
        l.set_alpha(3, 7, str(data.get("secuencia", "")).strip())

        # 8-9 tipo doc
        l.set_alpha(8, 9, str(data.get("tipo_doc", "")).strip())

        # 10-25 num doc (16 caracteres según Anexo Técnico campo 4)
        l.set_alpha(10, 25, str(data.get("num_doc", "")).strip())

        # 26-27 tipo cotizante / 28-29 subtipo
        l.set_alpha(26, 27, str(data.get("tipo_cotizante", "")).strip())
        l.set_alpha(28, 29, str(data.get("subtipo_cotizante", "")).strip())

        # 32-36 municipio (DANE)
        l.set_alpha(32, 36, str(data.get("municipio", "")).strip())

        # 37-56 primer apellido (20)
        l.set_alpha(37, 56, data.get("papellido", ""))

        # 57-86 segundo apellido (30)
        l.set_alpha(57, 86, data.get("sapellido", ""))

        # 87-106 primer nombre (20)
        l.set_alpha(87, 106, data.get("pnombre", ""))

        # 107-136 segundo nombre (30) - CORREGIDO según Anexo Técnico
        l.set_alpha(107, 136, data.get("snombre", ""))

        # ============================================
        # Campos 15-30: Novedades (posiciones 137-153)
        # ============================================
        
        # Campo 15 (pos 137): ING - Ingreso
        l.set_alpha(137, 137, str(data.get("nov_ing", "")).strip())
        
        # Campo 16 (pos 138): RET - Retiro
        l.set_alpha(138, 138, str(data.get("nov_ret", "")).strip())
        
        # Campo 21 (pos 143): VSP - Variación permanente salario
        l.set_alpha(143, 143, str(data.get("nov_vsp", "")).strip())
        
        # Campo 23 (pos 145): VST - Variación transitoria salario
        l.set_alpha(145, 145, str(data.get("nov_vst", "")).strip())
        
        # Campo 24 (pos 146): SLN - Suspensión temporal
        l.set_alpha(146, 146, str(data.get("nov_sln", "")).strip())
        
        # Campo 25 (pos 147): IGE - Incapacidad enfermedad general
        l.set_alpha(147, 147, str(data.get("nov_ige", "")).strip())
        
        # Campo 26 (pos 148): LMA - Licencia maternidad/paternidad
        l.set_alpha(148, 148, str(data.get("nov_lma", "")).strip())
        
        # Campo 27 (pos 149): VAC - Vacaciones
        l.set_alpha(149, 149, str(data.get("nov_vac", "")).strip())
        
        # Campo 30 (pos 152-153): IRL - Días incapacidad AT/EL
        l.set_num(152, 153, int(str(data.get("irl_dias", 0)).strip() or 0))

        # 154-159 Campo 31: AFP (6 caracteres). En blanco si no obligado a pensiones.
        afp_val = data.get("afp") or ""
        l.set_alpha(154, 159, str(afp_val).strip())

        # 166-171 Campo 33: EPS (6 caracteres)
        l.set_alpha(166, 171, str(data.get("eps", "")).strip())

        # 178-183 Campo 35: CCF (6 caracteres)
        l.set_alpha(178, 183, str(data.get("ccf", "")).strip())

        # ✅ 1) Clonar lo NO mapeado (tail): 333-693
        raw_tail = data.get("raw_333_693")
        if raw_tail:
            l.set_raw(333, 693, raw_tail)

        # ✅ 2) Sobrescribir lo que sí estamos mapeando (184-332 y campos ARL 381-407, 507-513)

        # 184-191 días por subsistema (Layout: 36=pension 184-185, 37=salud 186-187)
        l.set_num(184, 185, int(str(data.get("dias_pension", 0)).zfill(2)))
        l.set_num(186, 187, int(str(data.get("dias_salud", 0)).zfill(2)))
        l.set_num(188, 189, int(str(data.get("dias_arl", 0)).zfill(2)))
        l.set_num(190, 191, int(str(data.get("dias_caja", 0)).zfill(2)))

        # 192-200 Campo 40: Salario básico (9 chars numéricos)
        l.set_num(192, 200, int(str(data.get("v_192_200", "")).strip() or 0))

        # 201 Campo 41: Tipo de salario (1 char: X=integral, F=fijo, V=variable)
        tipo_salario = str(data.get("tipo_salario", "F")).strip()  # Por defecto "F" si no se especifica
        l.set_alpha(201, 201, tipo_salario[:1] if tipo_salario else " ")

        # 202-210 Campo 42: IBC pensión (9 chars numéricos)
        l.set_num(202, 210, int(str(data.get("ibc_pension", "")).strip() or 0))

        # 211-219 Campo 43: IBC salud (9 chars numéricos)
        l.set_num(211, 219, int(str(data.get("v_210_218", "")).strip() or 0))

        # 220-228 Campo 44: IBC riesgos laborales (9 chars numéricos)
        l.set_num(220, 228, int(str(data.get("v_219_227", "")).strip() or 0))

        # 229-237 Campo 45: IBC CCF (9 chars numéricos)
        l.set_num(229, 237, int(str(data.get("v_228_236", "")).strip() or 0))

        # 238-244 Campo 46: Tarifa aportes pensiones (7 chars con decimales)
        l.set_alpha(238, 244, str(data.get("v_237_245", "")).strip())

        # 245-253 Campo 47: Cotización obligatoria pensiones (9 chars numéricos)
        l.set_num(245, 253, int(str(data.get("v_246_254", "")).strip() or 0))

        # 254-262 Campo 48: Aporte voluntario afiliado pensiones (9 chars numéricos)
        l.set_num(254, 262, int(str(data.get("v_255_263", "")).strip() or 0))

        # 263-271 Campo 49: Aporte voluntario aportante pensiones (9 chars numéricos)
        l.set_num(263, 271, int(str(data.get("v_264_272", "")).strip() or 0))

        # 272-280 Campo 50: Total cotización pensiones (9 chars numéricos)
        l.set_num(272, 280, int(str(data.get("v_273_281", "")).strip() or 0))

        # 281-289 Campo 51: Fondo solidaridad - solidaridad (9 chars numéricos)
        l.set_num(281, 289, int(str(data.get("v_282_290", "")).strip() or 0))

        # 290-298 Campo 52: Fondo solidaridad - subsistencia (9 chars numéricos)
        l.set_num(290, 298, int(str(data.get("v_291_299", "")).strip() or 0))

        # 299-307 Campo 53: Valor no retenido (9 chars numéricos)
        l.set_num(299, 307, int(str(data.get("v_300_308", "")).strip() or 0))

        # 308-314 Campo 54: Tarifa aportes salud (7 chars con decimales)
        l.set_alpha(308, 314, str(data.get("v_309_317", "")).strip())

        # 315-323 Campo 55: Cotización obligatoria salud (9 chars numéricos)
        l.set_num(315, 323, int(str(data.get("v_318_326", "")).strip() or 0))

        # 324-332 Campo 56: UPC adicional (9 chars numéricos)
        l.set_num(324, 332, int(str(data.get("v_327_332", "")).strip() or 0))

        # 348-356 (9) (si lo estás pasando; si no, queda lo del tail)
        v348 = str(data.get("v_348_356", "")).strip()
        if v348 != "":
            l.set_num(348, 356, int(v348 or 0))

        # ===================================================================
        # CAMPOS ARL (zona 333-693)
        # ===================================================================
        
        # 381-389 Campo 61: Tarifa aportes riesgos laborales (9 chars)
        tarifa_arl = str(data.get("tarifa_arl", "")).strip()
        if tarifa_arl:
            l.set_alpha(381, 389, tarifa_arl[:9].ljust(9, '0'))
        
        # 390-398 Campo 62: Centro de trabajo (9 chars, numérico). Siempre escribir (0, 1, 3 o 5).
        centro_trabajo = data.get("centro_trabajo", 0)
        if centro_trabajo is None or centro_trabajo == "":
            centro_trabajo = 0
        l.set_num(390, 398, int(centro_trabajo))
        
        # 399-407 Campo 63: Cotización obligatoria riesgos laborales (9 chars, numérico)
        cotizacion_arl = str(data.get("cotizacion_arl", "")).strip()
        if cotizacion_arl:
            l.set_num(399, 407, int(float(cotizacion_arl)))
        
        # 408-414 Campo 64: Tarifa aportes CCF (7 chars, formato decimal: 0.04000 = 4%)
        tarifa_ccf = str(data.get("tarifa_ccf", "")).strip()
        if tarifa_ccf:
            # Si viene en formato "4.00000" (porcentaje), convertir a "0.04000" (decimal)
            if tarifa_ccf.startswith("4.") and len(tarifa_ccf) == 7:
                tarifa_ccf = "0.04000"
            elif tarifa_ccf.startswith("2.") and len(tarifa_ccf) == 7:
                tarifa_ccf = "0.02000"
            elif tarifa_ccf.startswith("3.") and len(tarifa_ccf) == 7:
                tarifa_ccf = "0.03000"
            l.set_alpha(408, 414, tarifa_ccf)
        
        # 415-423 Campo 65: Valor aporte CCF (9 chars, numérico)
        valor_ccf = str(data.get("valor_ccf", "")).strip()
        if valor_ccf:
            l.set_num(415, 423, int(float(valor_ccf)))
        
        # 424-430 Campo 66: Tarifa aportes SENA (7 chars, numérico con decimales)
        tarifa_sena = str(data.get("tarifa_sena", "")).strip()
        if tarifa_sena:
            l.set_alpha(424, 430, tarifa_sena)
        
        # 431-439 Campo 67: Valor aportes SENA (9 chars, numérico)
        valor_sena = str(data.get("valor_sena", "")).strip()
        if valor_sena:
            l.set_num(431, 439, int(float(valor_sena)))
        
        # 440-446 Campo 68: Tarifa aportes ICBF (7 chars, numérico con decimales)
        tarifa_icbf = str(data.get("tarifa_icbf", "")).strip()
        if tarifa_icbf:
            l.set_alpha(440, 446, tarifa_icbf)
        
        # 447-455 Campo 69: Valor aporte ICBF (9 chars, numérico)
        valor_icbf = str(data.get("valor_icbf", "")).strip()
        if valor_icbf:
            l.set_num(447, 455, int(float(valor_icbf)))
        
        # 506 Campo 76: Cotizante exonerado salud, SENA e ICBF (1 char, S/N)
        exonerado = str(data.get("exonerado", "")).strip()
        if exonerado:
            l.set_alpha(506, 506, exonerado[:1])
        
        # 507-512 Campo 77: Código administradora riesgos laborales (6 chars, alfanumérico)
        codigo_arl = str(data.get("codigo_arl", "")).strip()
        if codigo_arl:
            l.set_alpha(507, 512, codigo_arl)
        
        # 513 Campo 78: Clase de riesgo (1 char, pos 513: 1-5 según tarifa ARL 0.522→1, 1.044→2, 2.436→3, 4.350→4, 6.960→5)
        clase_riesgo = str(data.get("clase_riesgo", "")).strip()
        if clase_riesgo not in ("1", "2", "3", "4", "5"):
            clase_riesgo = "1"
        l.set_alpha(513, 513, clase_riesgo[:1])
        
        # 665-673 Campo 95: IBC otros parafiscales (no CCF). Obligatorio tipos 1,18,20,22,30,31,55
        # Error 816: no puede ser 0 cuando hay aporte SENA/ICBF y 30 días cotizados
        ibc_otros_paraf = data.get("ibc_otros_parafiscales")
        if ibc_otros_paraf is not None and int(ibc_otros_paraf) >= 0:
            l.set_num(665, 673, int(ibc_otros_paraf))

        # 674-676 Campo 96: Número de horas laboradas (3 chars, numérico)
        horas_laboradas = str(data.get("horas_laboradas", "")).strip()
        if horas_laboradas:
            l.set_num(674, 676, int(horas_laboradas or 0))
        
        # ===================================================================
        # CAMPOS DE FECHAS DE NOVEDADES (zona 515-664, campos 80-94)
        # ===================================================================
        
        # Campo 80 (pos 515-524): Fecha ingreso (AAAA-MM-DD)
        fecha_ing = str(data.get("fecha_ing", "")).strip()
        if fecha_ing:
            l.set_alpha(515, 524, fecha_ing[:10])
        
        # Campo 81 (pos 525-534): Fecha retiro (AAAA-MM-DD)
        fecha_ret = str(data.get("fecha_ret", "")).strip()
        if fecha_ret:
            l.set_alpha(525, 534, fecha_ret[:10])
        
        # Campo 82 (pos 535-544): Fecha inicio VSP (AAAA-MM-DD)
        fecha_vsp = str(data.get("fecha_vsp_inicio", "")).strip()
        if fecha_vsp:
            l.set_alpha(535, 544, fecha_vsp[:10])
        
        # Campo 83 (pos 545-554): Fecha inicio SLN (AAAA-MM-DD)
        fecha_sln_inicio = str(data.get("fecha_sln_inicio", "")).strip()
        if fecha_sln_inicio:
            l.set_alpha(545, 554, fecha_sln_inicio[:10])
        
        # Campo 84 (pos 555-564): Fecha fin SLN (AAAA-MM-DD)
        fecha_sln_fin = str(data.get("fecha_sln_fin", "")).strip()
        if fecha_sln_fin:
            l.set_alpha(555, 564, fecha_sln_fin[:10])
        
        # Campo 85 (pos 565-574): Fecha inicio IGE (AAAA-MM-DD)
        fecha_ige_inicio = str(data.get("fecha_ige_inicio", "")).strip()
        if fecha_ige_inicio:
            l.set_alpha(565, 574, fecha_ige_inicio[:10])
        
        # Campo 86 (pos 575-584): Fecha fin IGE (AAAA-MM-DD)
        fecha_ige_fin = str(data.get("fecha_ige_fin", "")).strip()
        if fecha_ige_fin:
            l.set_alpha(575, 584, fecha_ige_fin[:10])
        
        # Campo 87 (pos 585-594): Fecha inicio LMA (AAAA-MM-DD)
        fecha_lma_inicio = str(data.get("fecha_lma_inicio", "")).strip()
        if fecha_lma_inicio:
            l.set_alpha(585, 594, fecha_lma_inicio[:10])
        
        # Campo 88 (pos 595-604): Fecha fin LMA (AAAA-MM-DD)
        fecha_lma_fin = str(data.get("fecha_lma_fin", "")).strip()
        if fecha_lma_fin:
            l.set_alpha(595, 604, fecha_lma_fin[:10])
        
        # Campo 89 (pos 605-614): Fecha inicio VAC (AAAA-MM-DD)
        fecha_vac_inicio = str(data.get("fecha_vac_inicio", "")).strip()
        if fecha_vac_inicio:
            l.set_alpha(605, 614, fecha_vac_inicio[:10])
        
        # Campo 90 (pos 615-624): Fecha fin VAC (AAAA-MM-DD)
        fecha_vac_fin = str(data.get("fecha_vac_fin", "")).strip()
        if fecha_vac_fin:
            l.set_alpha(615, 624, fecha_vac_fin[:10])
        
        # Campo 93 (pos 645-654): Fecha inicio IRL (AAAA-MM-DD)
        fecha_irl_inicio = str(data.get("fecha_irl_inicio", "")).strip()
        if fecha_irl_inicio:
            l.set_alpha(645, 654, fecha_irl_inicio[:10])
        
        # Campo 94 (pos 655-664): Fecha fin IRL (AAAA-MM-DD)
        fecha_irl_fin = str(data.get("fecha_irl_fin", "")).strip()
        if fecha_irl_fin:
            l.set_alpha(655, 664, fecha_irl_fin[:10])
        
        # 687-693 Campo 98: Actividad económica riesgos laborales (7 chars, numérico)
        actividad_economica = str(data.get("actividad_economica_arl", "")).strip()
        if actividad_economica:
            # Asegurar que solo se escriban exactamente 7 caracteres
            if len(actividad_economica) > 7:
                actividad_economica = actividad_economica[:7]
            elif len(actividad_economica) < 7:
                # Rellenar con ceros a la izquierda (es numérico)
                actividad_economica = actividad_economica.zfill(7)
            l.set_alpha(687, 693, actividad_economica)

        # Renderizar y validar longitud
        rendered = l.render()
        
        # WORKAROUND: Si la línea tiene 694 caracteres, truncar el último
        # (bug conocido en algunas líneas específicas)
        if len(rendered) == 694:
            rendered = rendered[:693]
        elif len(rendered) != 693:
            raise ValueError(f"Línea generada tiene {len(rendered)} caracteres, esperado 693")
        
        return rendered