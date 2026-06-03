"""Exploração: encontrar os fundos da teia no Informe Mensal de FIDC, por CNPJ E por nome."""
import io, os, re, zipfile
import requests
import pandas as pd

BASE = "https://dados.cvm.gov.br/dados/FIDC/DOC/INF_MENSAL/DADOS/inf_mensal_fidc_{}.zip"
MESES = [f"2025{m:02d}" for m in range(1, 13)] + [f"2026{m:02d}" for m in range(1, 5)]
CACHE = "data/cvm_fidc_mensal"
os.makedirs(CACHE, exist_ok=True)

ALVO_CNPJ = {
    "46909301000133": "SDG II",
    "53273475000118": "Anna",
    "32088041000178": "Hans 95",
    "29786909000107": "Lancia!",
    "53311600000137": "Termopilas",
    "34081900000122": "Gold Style",
    "42584801000191": "Maranta",
}
NOMES = re.compile(r"\bSDG\b|HANS\s*95|\bANNA\b|LANCIA|TERM[OÓ]PILAS|GOLD\s*STYLE|MARANTA", re.I)


def get(ym):
    c = f"{CACHE}/inf_mensal_fidc_{ym}.zip"
    if os.path.exists(c):
        return open(c, "rb").read()
    b = requests.get(BASE.format(ym), timeout=180).content
    open(c, "wb").write(b)
    return b


def norm(s):
    return re.sub(r"\D", "", str(s))


def main():
    hits = {}
    for ym in MESES:
        zf = zipfile.ZipFile(io.BytesIO(get(ym)))
        df = pd.read_csv(zf.open(f"inf_mensal_fidc_tab_I_{ym}.csv"),
                         sep=";", encoding="latin-1", dtype=str)
        df["c"] = df["CNPJ_FUNDO_CLASSE"].map(norm)
        m = df[df.c.isin(ALVO_CNPJ) | df.DENOM_SOCIAL.str.contains(NOMES, na=False)]
        for _, r in m.iterrows():
            k = (r.c, r["DENOM_SOCIAL"][:60])
            hits.setdefault(k, []).append(ym)

    print("=== fundos da teia no Informe Mensal FIDC (por CNPJ OU nome) ===")
    for (c, nome), mm in sorted(hits.items(), key=lambda x: -len(x[1])):
        marca = "  <-- ALVO" if c in ALVO_CNPJ else ""
        print(f"  {c} | {len(mm):2}m [{mm[0]}..{mm[-1]}] | {nome}{marca}")

    print("\n=== alvos NÃO encontrados em nenhum mês ===")
    achados = {c for (c, _), _ in hits.items()}
    for c, nome in ALVO_CNPJ.items():
        if c not in achados:
            print(f"  AUSENTE: {nome} ({c})")


if __name__ == "__main__":
    main()
