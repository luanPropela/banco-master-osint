"""Investiga ONDE vive 'administrador' e 'gestor' de FIDC de forma programatica.
(a) colunas ADMIN/GEST no Informe Mensal; (b) subdiretorios abertos de FIDC;
(c) cad_fi.csv cobre o SDG II e tem gestor?"""
import io, os, re, zipfile
import requests
import pandas as pd

H = {"User-Agent": "Mozilla/5.0"}
SDG2 = "46909301000133"
CACHE = "data/cvm_fidc_mensal"


def secao(t):
    print("\n" + "=" * 70 + f"\n{t}\n" + "=" * 70)


def a_informe_colunas():
    secao("(a) Colunas com ADMIN/GEST no Informe Mensal de FIDC (202603)")
    z = f"{CACHE}/inf_mensal_fidc_202603.zip"
    if not os.path.exists(z):
        print("  (cache 202603 ausente — rode explore_fidc.py antes)"); return
    zf = zipfile.ZipFile(z)
    for n in zf.namelist():
        head = zf.open(n).readline().decode("latin-1")
        cols = [c.strip() for c in head.split(";")]
        achados = [c for c in cols if "ADMIN" in c.upper() or "GEST" in c.upper()]
        if achados:
            print(f"  {n}: {achados}")


def b_diretorios_fidc():
    secao("(b) Subdiretorios abertos em dados.cvm.gov.br/dados/FIDC/")
    for sub in ["", "CAD/DADOS/", "DOC/INF_MENSAL/DADOS/", "DOC/INF_TRIMESTRAL/DADOS/", "CAD/"]:
        url = f"https://dados.cvm.gov.br/dados/FIDC/{sub}"
        try:
            r = requests.get(url, headers=H, timeout=40)
            arqs = sorted(set(re.findall(r'href="([^"?][^"]*\.(?:csv|zip))"', r.text)))
            dirs = sorted(set(re.findall(r'href="([A-Z][^"]*/)"', r.text)))
            print(f"  {url} -> {r.status_code} | arquivos={arqs[:6]} | dirs={dirs[:8]}")
        except Exception as e:
            print(f"  {url} -> ERRO {e}")


def c_cad_fi():
    secao("(c) cad_fi.csv cobre o SDG II? tem coluna de gestor?")
    url = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
    cache = "data/cad_fi.csv"
    if not os.path.exists(cache):
        print("  baixando cad_fi.csv ...")
        r = requests.get(url, headers=H, timeout=180)
        open(cache, "wb").write(r.content)
    df = pd.read_csv(cache, sep=";", encoding="latin-1", dtype=str, low_memory=False)
    print(f"  linhas={len(df)} | colunas={list(df.columns)}")
    df["c"] = df.get("CNPJ_FUNDO", df.columns[0]).astype(str).str.replace(r"\D", "", regex=True)
    sub = df[df.c == SDG2]
    print(f"  SDG II presente em cad_fi? {'SIM' if len(sub) else 'NAO'}")
    if len(sub):
        r = sub.iloc[0]
        for col in df.columns:
            if any(k in col.upper() for k in ("ADMIN", "GEST", "CUSTO", "AUDITOR", "TP_FUNDO", "SIT")):
                print(f"     {col:20} = {r[col]}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    a_informe_colunas()
    b_diretorios_fidc()
    c_cad_fi()
