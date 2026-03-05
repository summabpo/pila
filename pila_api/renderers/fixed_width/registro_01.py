# pila_api/renderers/fixed_width/registro_01.py

from pila_api.renderers.fixed_width.base import FixedWidthLine


class Registro01Renderer:
    """
    Registro tipo 1 del archivo tipo 2 – Encabezado (359 caracteres).
    Referencia: Anexo Técnico 2 v.29, ARCHIVO TIPO 2 - Información planilla integrada.
    Ver pila/docs/ARCHIVO_TIPO2_ENCABEZADO.md.
    """
    LEN = 359

    def render(self, data: dict) -> str:
        """
        data: dict con las claves usadas por generar_txt para el encabezado.
        Campos del layout (posiciones 1-based):
          1-2 tipo_registro, 3 modalidad_planilla, 4-7 secuencia,
          8-207 razon_social, 208-209 tipo_doc, 210-225 num_doc, 226 dv,
          227 tipo_planilla, 228-237 numero_planilla_asociada, 238-247 fecha_pago_planilla_asociada,
          248 forma_presentacion, 249-258 codigo_sucursal, 259-298 nombre_sucursal,
          299-304 codigo_arl, 305-311 periodo_pago_no_salud, 312-318 periodo_pago_salud,
          319-328 numero_radicacion, 329-338 fecha_pago, 339-343 total_cotizantes,
          344-355 valor_total_nomina, 356-357 tipo_aportante, 358-359 codigo_operador.
        """
        l = FixedWidthLine(self.LEN)

        # --- Campos 1-3 ---
        l.set_alpha(1, 2, "01")  # Campo 1: tipo registro
        l.set_alpha(3, 3, str(data.get("modalidad_planilla", "1"))[:1])  # Campo 2: modalidad (1=Electrónica, 2=Asistida)
        sec = str(data.get("secuencia", "0001")).strip()[:4].zfill(4)
        l.set_alpha(4, 7, sec)  # Campo 3: secuencia 0001

        # --- Campos 4-8 ---
        razon = str(data.get("razon_social", ""))[:200]
        l.set_alpha(8, 207, razon)  # Campo 4: razón social (200)
        l.set_alpha(208, 209, str(data.get("tipo_doc", "NI"))[:2].ljust(2))  # Campo 5: tipo documento
        num_doc = str(data.get("num_doc", "")).strip()[:16].ljust(16)  # Campo 6: 16 chars A
        l.set_alpha(210, 225, num_doc)
        dv = str(data.get("dv", "")).strip()[:1] or " "
        l.set_alpha(226, 226, dv)  # Campo 7: dígito verificación
        l.set_alpha(227, 227, str(data.get("tipo_planilla", "E"))[:1])  # Campo 8: tipo planilla

        # --- Campos 9-10 ---
        num_planilla_asoc = str(data.get("numero_planilla_asociada", "")).strip()[:9]
        l.set_alpha(228, 237, num_planilla_asoc.ljust(9))  # Campo 9: en blanco para E, K, etc.
        fecha_planilla_asoc = str(data.get("fecha_pago_planilla_asociada", "")).strip()[:10]
        l.set_alpha(238, 247, fecha_planilla_asoc.ljust(10))  # Campo 10

        # --- Campos 11-13 ---
        l.set_alpha(248, 248, str(data.get("forma_presentacion", "U"))[:1])  # Campo 11
        cod_suc = str(data.get("codigo_sucursal", "")).strip()[:10].ljust(10)
        l.set_alpha(249, 258, cod_suc)  # Campo 12
        nom_suc = str(data.get("nombre_sucursal", "")).strip()[:40].ljust(40)
        l.set_alpha(259, 298, nom_suc)  # Campo 13

        # --- Campos 14-16 ---
        cod_arl = str(data.get("codigo_arl", "")).strip()[:6].ljust(6)
        l.set_alpha(299, 304, cod_arl)  # Campo 14
        l.set_alpha(305, 311, str(data.get("periodo_pago_no_salud", "")).strip()[:7].ljust(7))  # Campo 15
        l.set_alpha(312, 318, str(data.get("periodo_pago_salud", "")).strip()[:7].ljust(7))  # Campo 16

        # --- Campos 17-18 ---
        num_rad = data.get("numero_radicacion")
        if num_rad is not None and str(num_rad).strip() != "":
            l.set_num(319, 328, int(num_rad))
        else:
            l.set_alpha(319, 328, "".ljust(10))  # en blanco si no asignado
        fecha_pago = str(data.get("fecha_pago", "")).strip()[:10].ljust(10)
        l.set_alpha(329, 338, fecha_pago)  # Campo 18

        # --- Campos 19-22 ---
        l.set_num(339, 343, int(data.get("total_cotizantes", 0)))  # Campo 19
        l.set_num(344, 355, int(data.get("valor_total_nomina", 0)))  # Campo 20
        tipo_ap = str(data.get("tipo_aportante", "01"))[:2].zfill(2)
        l.set_alpha(356, 357, tipo_ap)  # Campo 21
        cod_op = str(data.get("codigo_operador", "00"))[:2].zfill(2)
        l.set_num(358, 359, int(cod_op) if cod_op.isdigit() else 0)  # Campo 22 (2 dígitos)

        return l.render()
