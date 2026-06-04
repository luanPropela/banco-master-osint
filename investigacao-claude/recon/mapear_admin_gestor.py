"""
Mapeia ADMINISTRADOR + GESTOR (+ custodiante/auditor quando houver) de QUALQUER fundo,
de forma programática, a partir do cadastro unificado RCVM 175 da CVM.

Fonte: https://dados.cvm.gov.br/dados/FI/CAD/DADOS/registro_fundo_classe.zip  (registro_fundo.csv)
       — 88k fundos, cobre FI, FIDC, FIP, FII. Sem scraping.
Cross-check do administrador com o Informe Mensal de FIDC (Tab I).

Uso: roda da raiz do repo. Lê os CNPJs de investigacao-claude/dados/dataset_carlyle_csv/01_empresas.csv
e escreve investigacao-claude/dados/registro_admin_gestor_fundos.csv
"""
import io, os, re, zipfile
from collections import Counter
import requests
import pandas as pd

H = {"User-Agent": "Mozilla/5.0"}
ZIP_URL = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/registro_fundo_classe.zip"
EMPRESAS = "investigacao-claude/dados/dataset_carlyle_csv/01_empresas.csv"
OUT = "investigacao-claude/dados/registro_admin_gestor_fundos.csv"
FIDC_CACHE = "data/cvm_fidc_mensal"


def norm(s):
    return re.sub(r"\D", "", str(s))


def carregar_registro():
    cache = "data/registro_fundo_classe.zip"
    if not os.path.exists(cache):
        print("baixando registro_fundo_classe.zip ...")
        open(cache, "wb").write(requests.get(ZIP_URL, headers=H, timeout=240).content)
    zf = zipfile.ZipFile(cache)
    df = pd.read_csv(zf.open("registro_fundo.csv"), sep=";", encoding="latin-1", dtype=str, low_memory=False)
    df["c"] = df["CNPJ_Fundo"].map(norm)
    return df


def admin_do_informe_fidc():
    """administrador por CNPJ a partir do Informe Mensal de FIDC (cross-check)."""
    out = {}
    for f in sorted(os.listdir(FIDC_CACHE)) if os.path.isdir(FIDC_CACHE) else []:
        if not f.endswith(".zip"):
            continue
        ym = re.search(r"(\d{6})", f).group(1)
        try:
            zf = zipfile.ZipFile(f"{FIDC_CACHE}/{f}")
            d = pd.read_csv(zf.open(f"inf_mensal_fidc_tab_I_{ym}.csv"), sep=";", encoding="latin-1", dtype=str)
        except Exception:
            continue
        d["c"] = d["CNPJ_FUNDO_CLASSE"].map(norm)
        for _, r in d.iterrows():
            out[r["c"]] = (r.get("ADMIN") or "").strip()  # último mês vence
    return out


def main():
    reg = carregar_registro()
    cnpjs = sorted({norm(c) for c in pd.read_csv(EMPRESAS, dtype=str)["cnpj"]})
    informe_admin = admin_do_informe_fidc()

    cols = {
        "c": "cnpj", "Denominacao_Social": "fundo", "Tipo_Fundo": "tipo",
        "Situacao": "situacao", "CNPJ_Administrador": "cnpj_admin", "Administrador": "administrador",
        "CPF_CNPJ_Gestor": "cnpj_gestor", "Gestor": "gestor",
    }
    sub = reg[reg.c.isin(cnpjs)].copy()
    have = [k for k in cols if k in sub.columns]
    sub = sub[have].rename(columns={k: cols[k] for k in have})
    # cross-check com informe
    sub["admin_informe_fidc"] = sub["cnpj"].map(informe_admin).fillna("")
    sub = sub.sort_values("gestor", na_position="last")
    sub.to_csv(OUT, index=False, encoding="utf-8-sig")

    print(f"{len(sub)} fundos do perímetro encontrados no registro_fundo (de {len(cnpjs)} CNPJs).")
    print(f"-> {OUT}\n")
    pd.set_option("display.max_colwidth", 38); pd.set_option("display.width", 200)
    print(sub[["fundo", "situacao", "administrador", "gestor"]].to_string(index=False))

    print("\n=== concentração por GESTOR (a 'teia') ===")
    for g, n in Counter(sub["gestor"].fillna("(sem gestor)")).most_common():
        print(f"  {n:2}x  {g}")
    print("\n=== concentração por ADMINISTRADOR ===")
    for a, n in Counter(sub["administrador"].fillna("(sem admin)")).most_common():
        print(f"  {n:2}x  {a}")


if __name__ == "__main__":
    main()
