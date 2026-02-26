# pila_api/renderers/fixed_width/base.py
from decimal import Decimal


class FixedWidthLine:
    """
    Utilidad para construir líneas de ancho fijo (1-indexado),
    como las exigidas por PILA (registros tipo 01 / 02).
    """

    def __init__(self, length: int):
        self.length = length
        self._buf = [" "] * length

    def set(self, start: int, end: int, value, align="left", pad=" "):
        """
        Escribe value en posiciones start..end (inclusive).
        start/end son 1-indexados (como PILA).
        """
        if start < 1 or end > self.length:
            raise ValueError(f"Slice fuera de rango: {start}-{end}")

        width = end - start + 1
        txt = "" if value is None else str(value)

        if len(txt) > width:
            raise ValueError(f"Valor '{txt}' excede ancho {width}")

        if align == "right":
            txt = txt.rjust(width, pad)
        else:
            txt = txt.ljust(width, pad)

        self._buf[start - 1:end] = list(txt)

    def set_num(self, start: int, end: int, value):
        """
        Numérico sin separadores, alineado a la derecha, padding con 0.
        """
        if value is None:
            value = 0

        if isinstance(value, Decimal):
            value = int(value)

        self.set(start, end, value, align="right", pad="0")

    def set_alpha(self, start: int, end: int, value):
        """
        Alfanumérico alineado a la izquierda, padding con espacio.
        """
        self.set(start, end, value, align="left", pad=" ")

    def set_raw(self, start: int, end: int, raw: str):
        """
        Copia literal raw al slice start..end (1-indexado, end inclusive).
        Útil para clonar segmentos mientras mapeamos semántica.
        """
        if start < 1 or end > self.length:
            raise ValueError(f"Slice fuera de rango: {start}-{end}")

        if raw is None:
            raw = ""

        raw = str(raw)
        width = end - start + 1

        if len(raw) != width:
            raise ValueError(f"raw debe medir {width}, pero mide {len(raw)}")

        self._buf[start - 1:end] = list(raw)

    def render(self) -> str:
        line = "".join(self._buf)
        if len(line) != self.length:
            raise ValueError("Longitud final incorrecta")
        return line