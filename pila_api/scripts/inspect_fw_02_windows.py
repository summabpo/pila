from pathlib import Path
import sys

def show_window(line, start, end):
    # start/end 1-indexados inclusive
    s = max(1, start)
    e = min(len(line), end)
    frag = line[s-1:e]
    print(f"[{s:>3}-{e:<3}] |{frag}|")

def main():
    txt_path = sys.argv[1]
    lines = Path(txt_path).read_text(errors="ignore").splitlines()
    lines = [l for l in lines if l.strip() and l.startswith("02")]

    if not lines:
        print("No encontré líneas tipo 02")
        return

    # toma 1 ejemplo
    line = lines[0]
    print("\n=== PUNTO 29: BLOQUES 320-332 y 348-356 ===")
    print("320-332:", repr(line[319:332]))  # 320..332 => [319:332]
    print("333-347:", repr(line[332:347]))  # ya lo tienes, pero lo repetimos
    print("348-356:", repr(line[347:356]))  # 348..356 => [347:356]
    show_window(line, 312, 360)            # un poquito más de contexto
    # --- Punto 28: inspección 333–347 ---
    print("\n=== PUNTO 28: BLOQUE 333-347 ===")
    print("333-347:", repr(line[332:347]))  # 333..347 (1-index) => [332:347]
    show_window(line, 320, 360)           # contexto
    block = line[191:332]  # 192..332 (1-index) => [191:332]
    print("\n=== RULER 192-332 ===")
    print("len block:", len(block))

    # imprime en grupos de 9 y te dice el rango real 1-index
    pos = 192
    i = 0
    while i < len(block):
        chunk = block[i:i+9]
        print(f"{pos:>3}-{pos+len(chunk)-1:<3}  {chunk!r}")
        i += 9
        pos += 9
    # ventanas grandes para ubicar bloques (ajustamos después)
    windows = [
        (1, 40),
        (41, 80),
        (81, 120),
        (121, 180),
        (181, 240),
        (241, 300),
        (301, 360),
        (361, 420),
        (421, 480),
        (481, 540),
        (541, 600),
        (601, len(line)),
    ]
    print("\nVENTANAS:")
    for a, b in windows:
        show_window(line, a, b)

    # --- zoom al bloque 184..332 ---
    start, end = 184, 332
    frag = line[start-1:end]  # python slice
    print("\nZOOM 184-332:")
    print(f"[{start}-{end}] len={len(frag)} |{frag}|")
    
    d = line[183:191]  # 184-191
    print("\nPASO 1 - DIAS (184-191):", repr(d))
    print("salud :", d[0:2])
    print("pension:", d[2:4])
    print("arl   :", d[4:6])
    print("caja  :", d[6:8])

    print("\nSUBSLICES CLAVE:")
    print("184-191 (8):", repr(line[183:191]))   # 184..191
    print("192-200 (9):", repr(line[191:200]))   # 192..200
    print("201-209 (9):", repr(line[200:209]))   # 201..209
    print("210-218 (9):", repr(line[209:218]))   # 210..218

    print("\nBLOQUE 184–332:")
    show_window(line, 184, 332)
    
    from collections import Counter

    def sl(l, a, b):
        # a..b 1-index inclusive
        return l[a-1:b]

    # analiza slices 192-200 y vecinos en TODAS las líneas tipo 02
    c_192_200 = Counter(sl(l, 192, 200) for l in lines)
    c_201_209 = Counter(sl(l, 201, 209) for l in lines)
    c_210_218 = Counter(sl(l, 210, 218) for l in lines)

    print("\nPASO 2 - TOP 10 slice 192-200:")
    for v, n in c_192_200.most_common(10):
        print(repr(v), "=>", n)

    print("\nVecinos (para contexto): 201-209 TOP 5")
    for v, n in c_201_209.most_common(5):
        print(repr(v), "=>", n)

    print("\nVecinos (para contexto): 210-218 TOP 5")
    for v, n in c_210_218.most_common(5):
        print(repr(v), "=>", n)

if __name__ == "__main__":
    main()