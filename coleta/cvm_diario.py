import io
import sqlite3
import zipfile
from datetime import date
from pathlib import Path

import pandas as pd
import requests

DB_PATH = Path("data/master.db")
CACHE_DIR = Path("data/cvm_diario")
URL_TEMPLATE = "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{ym}.zip"
TIMEOUT = 120

FUNDOS_ALVO = {
    "02727085000130": "MAXIMA FMP-FGTS PETROBRAS",
    "03919474000120": "BANESTES FMP-FGTS PETROBRAS",
    "04894428000186": "BANESTES FMP-FGTS VALE DO RIO DOCE",
    "04894438000111": "MAXIMA FMP-FGTS VALE DO RIO DOCE",
}

PERIODO = ("2025-01", "2026-04")

SCHEMA = """
CREATE TABLE IF NOT EXISTS inf_diario (
    fundo_cnpj    TEXT NOT NULL,
    data          TEXT NOT NULL,
    pl            REAL,
    valor_cota    REAL,
    captacao_dia  REAL,
    resgate_dia   REAL,
    cotistas      INTEGER,
    PRIMARY KEY (fundo_cnpj, data)
);
CREATE INDEX IF NOT EXISTS idx_inf_diario_cnpj ON inf_diario(fundo_cnpj);
CREATE INDEX IF NOT EXISTS idx_inf_diario_data ON inf_diario(data);
"""

def gerar_meses(inicio: str, fim: str) -> list[str]:
    ano_i, mes_i = map(int, inicio.split("-"))
    ano_f, mes_f = map(int, fim.split("-"))
    meses = []
    ano, mes = ano_i, mes_i
    while (ano, mes) <= (ano_f, mes_f):
        meses.append(f"{ano:04d}{mes:02d}")
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1
    return meses

def baixar_zip(ym: str) -> bytes | None:
    cache = CACHE_DIR / f"inf_diario_fi_{ym}.zip"
    if cache.exists():
        return cache.read_bytes()
    url = URL_TEMPLATE.format(ym=ym)
    print(f"[DIARIO] baixando {url}")
    try:
        r = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException as e:
        print(f"[DIARIO] erro {ym}: {e}")
        return None
    if r.status_code != 200:
        print(f"[DIARIO] HTTP {r.status_code} para {ym}")
        return None
    cache.write_bytes(r.content)
    return r.content

def extrair_csv(zip_bytes: bytes, ym: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        nome_csv = next((n for n in zf.namelist() if n.endswith(".csv")), None)
        if not nome_csv:
            return pd.DataFrame()
        with zf.open(nome_csv) as f:
            return pd.read_csv(
                f, sep=";", encoding="latin-1", dtype=str,
                on_bad_lines="skip", low_memory=False,
            )

def normalizar(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    col_cnpj = "CNPJ_FUNDO_CLASSE" if "CNPJ_FUNDO_CLASSE" in df.columns else "CNPJ_FUNDO"
    if col_cnpj not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["__cnpj_norm"] = df[col_cnpj].astype(str).str.replace(r"\D", "", regex=True)
    df = df[df["__cnpj_norm"].isin(FUNDOS_ALVO.keys())].copy()
    if df.empty:
        return df
    df[col_cnpj] = df["__cnpj_norm"]
    df = df.drop(columns="__cnpj_norm")
    df = df.rename(columns={
        col_cnpj:         "fundo_cnpj",
        "DT_COMPTC":      "data",
        "VL_PATRIM_LIQ":  "pl",
        "VL_QUOTA":       "valor_cota",
        "CAPTC_DIA":      "captacao_dia",
        "RESG_DIA":       "resgate_dia",
        "NR_COTST":       "cotistas",
    })
    cols = ["fundo_cnpj", "data", "pl", "valor_cota",
            "captacao_dia", "resgate_dia", "cotistas"]
    df = df[[c for c in cols if c in df.columns]]
    for col in ("pl", "valor_cota", "captacao_dia", "resgate_dia"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "cotistas" in df.columns:
        df["cotistas"] = pd.to_numeric(df["cotistas"], errors="coerce").astype("Int64")
    return df

def inserir(con: sqlite3.Connection, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    registros = df.to_records(index=False).tolist()
    con.executemany("""
        INSERT OR REPLACE INTO inf_diario
            (fundo_cnpj, data, pl, valor_cota, captacao_dia, resgate_dia, cotistas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [tuple(r) for r in registros])
    return len(registros)

def resumo(con: sqlite3.Connection) -> None:
    print("\n[DIARIO] === RESUMO ===")
    (total,) = con.execute("SELECT COUNT(*) FROM inf_diario").fetchone()
    print(f"  linhas totais: {total}")
    rows = con.execute("""
        SELECT fundo_cnpj, MIN(data), MAX(data), COUNT(*),
               ROUND(AVG(pl)/1e6, 2), ROUND(AVG(cotistas), 0)
        FROM inf_diario GROUP BY fundo_cnpj
    """).fetchall()
    for cnpj, dmin, dmax, n, pl_med, cot_med in rows:
        nome = FUNDOS_ALVO.get(cnpj, cnpj)
        print(f"  {nome}")
        print(f"    período: {dmin} -> {dmax} ({n} dias)")
        print(f"    PL médio: R$ {pl_med}M  |  cotistas médio: {cot_med}")

def main() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    con.commit()

    meses = gerar_meses(*PERIODO)
    print(f"[DIARIO] janela: {meses[0]} a {meses[-1]} ({len(meses)} meses)")

    total_inseridas = 0
    for ym in meses:
        zip_bytes = baixar_zip(ym)
        if not zip_bytes:
            continue
        df = normalizar(extrair_csv(zip_bytes, ym))
        n = inserir(con, df)
        print(f"[DIARIO] {ym}: {n} linhas inseridas")
        total_inseridas += n
        con.commit()

    print(f"\n[DIARIO] total inserido nesta execução: {total_inseridas}")
    resumo(con)
    con.close()

if __name__ == "__main__":
    main()
