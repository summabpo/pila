# pila_api/renderers/fixed_width/registro_01.py

from pila_api.renderers.fixed_width.base import FixedWidthLine


class Registro01Renderer:
    """
    Registro tipo 01 - Encabezado PILA (ancho fijo)
    Basado en ATI_COL28736 (Aportes en Línea)

    Longitud observada en el ejemplo: 359
    """
    LEN = 359

    def render(self, data: dict) -> str:
        """
        data esperado (mínimo):
        {
          "codigo_3_7": "10001",
          "razon_social": "ATIEMPO S.A.S.",
          "tipo_doc": "NI",
          "num_doc": "890404383",
          "dv": "5",  # Dígito de verificación
          "flag_226": "1",
          "tipo_planilla": "E",
          "periodo_cotizacion": "2025-12",
          "periodo_pago": "2026-01",
          "forma_presentacion": "U",  # U=única, S=sucursal
          "codigo_arl": "ARL001",  # Código ARL del aportante (6 chars)
        }
        """
        l = FixedWidthLine(self.LEN)

        # 1-2 tipo registro
        l.set_alpha(1, 2, "01")

        # 3-7 (en tu ejemplo: 10001)
        l.set_alpha(3, 7, str(data.get("codigo_3_7", "")).strip())

        # 8-207 razón social (en el ejemplo el NIT arranca en 208)
        l.set_alpha(8, 207, data.get("razon_social", ""))

        # 208-209 tipo doc (NI)
        l.set_alpha(208, 209, data.get("tipo_doc", ""))

        # 210-218 num doc (relleno con ceros a la izquierda)
        num_doc_raw = str(data.get("num_doc", "")).strip()
        num_doc_int = int(num_doc_raw) if num_doc_raw.isdigit() else 0
        l.set_num(210, 218, num_doc_int)

        # 226 Campo 9: Dígito de verificación NIT (1 char)
        dv = str(data.get("dv", "")).strip()
        l.set_alpha(226, 226, dv[:1] if dv else " ")

        # 227 tipo planilla (E)
        l.set_alpha(227, 227, str(data.get("tipo_planilla", "E"))[:1])

        # 248 Campo 10: Forma de presentación (U=única, S=sucursal)
        forma_pres = str(data.get("forma_presentacion", "U"))[:1]
        l.set_alpha(248, 248, forma_pres)
        
        # 299-304 Campo 18: Código ARL del aportante (6 chars, obligatorio para planilla E)
        codigo_arl = str(data.get("codigo_arl", "")).strip()
        l.set_alpha(299, 304, codigo_arl[:6].ljust(6) if codigo_arl else "      ")

        # 305-311 periodo cotización AAAA-MM (7 chars)
        l.set_alpha(305, 311, data.get("periodo_cotizacion", ""))

        # 312-318 periodo pago AAAA-MM (7 chars)
        l.set_alpha(312, 318, data.get("periodo_pago", ""))

        # 339-343 Campo 19: Número total de cotizantes (5 chars numéricos)
        total_cotizantes = int(data.get("total_cotizantes", 0))
        l.set_num(339, 343, total_cotizantes)

        # 344-355 Campo 20: Valor total de la nómina (12 chars numéricos)
        valor_total_nomina = int(data.get("valor_total_nomina", 0))
        l.set_num(344, 355, valor_total_nomina)

        # 356-357 Campo 30: Tipo de aportante (2 chars: 01=empleador, 02=independiente, etc.)
        l.set_alpha(356, 357, str(data.get("tipo_aportante", "01"))[:2])

        # 358-359 Espacios finales (completar hasta 359 caracteres)
        l.set_alpha(358, 359, "  ")

        return l.render()