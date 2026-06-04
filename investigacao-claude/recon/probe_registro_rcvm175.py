"""Procura o GESTOR do SDG II no cadastro unificado RCVM 175 (registro_fundo/classe)
e lista todos os arquivos de cadastro abertos em FI/CAD/DADOS/."""
import io, os, re, zipfile
import requests
import pandas as pd

H = {"User-Agent": "Mozilla/5.0"}
SDG2 = "46909301000133"
BASE = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/"


def listar_dir():
    print("=== arquivos em FI/CAD/DADOS/ ===")
    r = requests.get(BASE, headers=H, timeout=60)
    arqs = sorted(set(re.findall(r'href="([^"?][^"]*\.(?:csv|zip))"', r.text)))
    for a in arqs:
        print("  ", a)
    return arqs


def baixar(nome):
    cache = f"data/{nome}"
    if os.path.exists(cache):
        return cache
    r = requests.get(BASE + nome, headers=H, timeout=180)
    if r.status_code == 200:
        open(cache, "wb").write(r.content)
        return cache
    print(f"   {nome} -> HTTP {r.status_code}")
    return None


def inspecionar(nome):
    path = baixar(nome)
    if not path:
        return
    # zip ou csv
    if nome.endswith(".zip"):
        zf = zipfile.ZipFile(path)
        nomes = zf.namelist()
        print(f"\n=== {nome} contém: {nomes}")
        for n in nomes:
            try:
                df = pd.read_csv(zf.open(n), sep=";", encoding="latin-1", dtype=str, low_memory=False)
            except Exception as e:
                print(f"   erro {n}: {e}"); continue
            checar(n, df)
    else:
        df = pd.read_csv(path, sep=";", encoding="latin-1", dtype=str, low_memory=False)
        checar(nome, df)


def checar(nome, df):
    col_cnpj = next((c for c in df.columns if "CNPJ" in c.upper() and ("FUNDO" in c.upper() or "CLASSE" in c.upper())), None)
    tem_gestor = [c for c in df.columns if "GEST" in c.upper()]
    print(f"\n--- {nome}: {len(df)} linhas | cnpj_col={col_cnpj} | cols_gestor={tem_gestor}")
    if not col_cnpj:
        print(f"      colunas: {list(df.columns)[:15]}")
        return
    df["c"] = df[col_cnpj].astype(str).str.replace(r"\D", "", regex=True)
    sub = df[df.c == SDG2]
    print(f"      SDG II presente? {'SIM' if len(sub) else 'nao'}")
    if len(sub):
        r = sub.iloc[0]
        for col in df.columns:
            if any(k in col.upper() for k in ("GEST", "ADMIN", "DENOM", "SIT", "TP_", "CATEG", "CLASSE_")):
                v = str(r[col])
                if v and v != "nan":
                    print(f"        {col:24} = {v}")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    arqs = listar_dir()
    # prioriza arquivos de registro unificado
    alvo = [a for a in arqs if "registro" in a.lower()] or arqs
    for a in alvo:
        inspecionar(a)
