from pathlib import Path
import re
import sys

def show_window(line, start, end):
    # start/end 1-indexados inclusive
    s = max(1, start)
    e = min(len(line), end)
    frag = line[s-1:e]
    print(f"[{s:>3}-{e:<3}] |{frag}|")

def chunks_with_pos(line: str):
    out = []
    for m in re.finditer(r"\S+", line):
        out.append((m.group(), m.start() + 1, m.end()))
    return out

def main():
    txt_path = sys.argv[1]
    tipo = sys.argv[2] if len(sys.argv) > 2 else None

    lines = Path(txt_path).read_text(errors="ignore").splitlines()
    lines = [l for l in lines if l.strip()]

    if tipo:
        lines = [l for l in lines if l.startswith(tipo)]
        if not lines:
            print(f"No encontré líneas tipo {tipo}")
            return

    tipos = sorted(set(l[:2] for l in lines))
    print("Tipos encontrados:", tipos)

    from collections import Counter
    c = Counter((l[:2], len(l)) for l in lines)
    print("Conteo (tipo, len):")
    for k, v in sorted(c.items()):
        print(" ", k, "=>", v)

    line = lines[0]
    print("\nEJEMPLO LINEA:")
    print("Tipo:", line[:2], "Len:", len(line))
    print(line[:200])

    print("\nVENTANAS CLAVE REG 01:")
    for a, b in [(1,30), (150,230), (220,260), (285,330), (330,359)]:
        show_window(line, a, b)

    print("\nTOKENS (valor, ini, fin):")
    for t in chunks_with_pos(line)[:80]:
        print(t)

if __name__ == "__main__":
    main()