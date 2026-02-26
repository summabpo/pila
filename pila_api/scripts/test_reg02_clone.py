from pathlib import Path
from pila_api.renderers.fixed_width.registro_02 import Registro02Renderer

txt = Path("pila_api/scripts/ATI_COL28736 (2).TXT").read_text(errors="ignore").splitlines()
line02 = next(l for l in txt if l.startswith("02") and l.strip())
orig = line02

renderer = Registro02Renderer()

data = {
    "secuencia": line02[2:7],
    "tipo_doc": line02[7:9],
    "num_doc": line02[9:17],
    "tipo_cotizante": line02[25:27],
    "subtipo_cotizante": line02[27:29],
    "municipio": line02[31:36],
    "papellido": line02[36:56],
    "sapellido": line02[56:86],
    "pnombre": line02[86:106],
    "snombre": line02[106:126],
    "flag_145": line02[144:145],
    "afp": line02[151:159],
    "eps": line02[165:171],
    "ccf": line02[177:182],

    "raw_333_693": line02[332:693],

    "dias_salud":   int(line02[183:185]),
    "dias_pension": int(line02[185:187]),
    "dias_arl":     int(line02[187:189]),
    "dias_caja":    int(line02[189:191]),

    "v_192_200": line02[191:200],  # 192-200
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

    "v_348_356": line02[347:356],
}

gen = renderer.render(data)

print("LEN orig:", len(orig), "LEN gen:", len(gen))
print("MATCH TOTAL?", orig == gen)

def eq(a, b):
    return orig[a-1:b] == gen[a-1:b]

print("MATCH 1-182?", eq(1, 182))
print("MATCH 184-332?", eq(184, 332))
print("MATCH 333-693?", eq(333, 693))
print("MATCH 348-356?", eq(348, 356))