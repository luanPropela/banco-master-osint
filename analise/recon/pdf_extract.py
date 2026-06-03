"""Extrai texto das DFs do SDG II e procura entidades/valores da matéria."""
import re
import sys
import pdfplumber

ALVOS = ["LORMONT", "BANVOX", "SUPER EMPREEND", "MASTER", "ANNA", "MKS",
         "HANS", "TANURE", "QUADRADO", "VORCARO", "DV HOLDING", "NGV",
         "DEBÊNTURE", "DEBENTURE", "CEDENTE", "COTISTA", "DIREITOS CRED"]


def extrair(path):
    full = []
    with pdfplumber.open(path) as pdf:
        for pg in pdf.pages:
            t = pg.extract_text() or ""
            full.append(t)
    return "\n".join(full)


def main():
    path = sys.argv[1]
    out_txt = path.rsplit(".", 1)[0] + ".txt"
    texto = extrair(path)
    open(out_txt, "w", encoding="utf-8").write(texto)
    print(f"[{path}] {len(texto)} chars de texto -> {out_txt}")
    linhas = texto.splitlines()
    print("\n=== linhas mencionando entidades/valores-alvo ===")
    seen = 0
    for i, ln in enumerate(linhas):
        up = ln.upper()
        if any(a in up for a in ALVOS):
            ctx = ln.strip()
            if ctx:
                print(f"  L{i:4}: {ctx[:160]}")
                seen += 1
        if seen > 80:
            print("  ... (truncado)")
            break
    if not seen:
        print("  (nenhum alvo encontrado — possível PDF escaneado/imagem)")


if __name__ == "__main__":
    main()
