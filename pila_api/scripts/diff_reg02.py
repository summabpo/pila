from pathlib import Path
from pila_api.renderers.fixed_width.registro_02 import Registro02Renderer


def first_diff_pos(a: str, b: str):
    for i, (x, y) in enumerate(zip(a, b), start=1):
        if x != y:
            return i
    if len(a) != len(b):
        return min(len(a), len(b)) + 1
    return None


def window(s: str, start: int, end: int):
    frag = s[start - 1 : end]
    return f"[{start}-{end}] |{frag}|"


def main():
    print("RUN diff_reg02.py ✅")

    txt_path = Path("pila_api/scripts/ATI_COL28736 (2).TXT")
    lines = txt_path.read_text(errors="ignore").splitlines()
    line02 = next(l for l in lines if l.startswith("02") and l.strip())

    renderer = Registro02Renderer()

    data = {
        "secuencia": line02[2:7],          # 3-7
        "tipo_doc": line02[7:9],           # 8-9
        "num_doc": line02[9:17],           # 10-17
        "tipo_cotizante": line02[25:27],   # 26-27
        "subtipo_cotizante": line02[27:29],# 28-29
        "municipio": line02[31:36],        # 32-36
        "papellido": line02[36:56],        # 37-56
        "sapellido": line02[56:86],        # 57-86
        "pnombre": line02[86:106],         # 87-106
        "snombre": line02[106:126],        # 107-126
        "flag_145": line02[144:145],       # 145
        "afp": line02[151:159],            # 152-159
        "eps": line02[165:171],            # 166-171
        "ccf": line02[177:182],            # 178-182

        # ✅ tail no mapeado
        "raw_333_693": line02[332:693],    # 333..693

        # ✅ 184-191 días
        "dias_salud":   int(line02[183:185]),
        "dias_pension": int(line02[185:187]),
        "dias_arl":     int(line02[187:189]),
        "dias_caja":    int(line02[189:191]),

        # ✅ 192-332 ruler
        "v_192_200": line02[191:200],
        "v_201_209": line02[200:209],
        "v_210_218": line02[209:218],
        "v_219_227": line02[218:227],
        "v_228_236": line02[227:236],
        "v_237_245": line02[236:245],
        "v_246_254": line02[245:254],
        "v_255_263": line02[254:263],
        "v_264_272": line02[263:272],
        "v_273_281": line02[272:281],
        "v_282_290": line02[281:290],
        "v_291_299": line02[290:299],
        "v_300_308": line02[299:308],
        "v_309_317": line02[308:317],
        "v_318_326": line02[317:326],
        "v_327_332": line02[326:332],

        # ✅ 348-356 (si lo quieres mapear ya)
        "v_348_356": line02[347:356],
    }

    gen = renderer.render(data)

    print("LEN orig:", len(line02), "LEN gen:", len(gen))
    pos = first_diff_pos(line02, gen)
    if pos is None:
        print("MATCH TOTAL ✅")
        return

    print("PRIMERA DIFERENCIA (pos 1-index):", pos)
    a = max(1, pos - 60)
    b = min(len(line02), pos + 60)

    print("\nORIG window:")
    print(window(line02, a, b))
    print("\nGEN  window:")
    print(window(gen, a, b))


if __name__ == "__main__":
    main()