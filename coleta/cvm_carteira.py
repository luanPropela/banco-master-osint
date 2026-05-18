import io
import sqlite3
import zipfile
from pathlib import Path

import pandas as pd
import requests

DB_PATH = Path("data/master.db")
CACHE_DIR = Path("data/cvm_carteira")
URL_TEMPLATE = "https://dados.cvm.gov.br/dados/FI/DOC/CDA/DADOS/cda_fi_{ym}.zip"

PERIODOS = ["202504", "202508", "202511"]
TIMEOUT = 180

SCHEMA = """
CREATE TABLE IF NOT EXISTS carteira (
    fundo_cnpj           TEXT NOT NULL,
    data_competencia     TEXT NOT NULL,
    tipo_aplicacao       TEXT,
    tipo_ativo           TEXT,
    emissor_ligado       TEXT,
    emissor_nome         TEXT,
    emissor_cnpj         TEXT,
    cod_ativo            TEXT,
    desc_ativo           TEXT,
    qt_pos_final         REAL,
    vl_merc_pos_final    REAL,
    vl_aquisicao         REAL,
    vl_venda             REAL,
    bloco                TEXT
);
CREATE INDEX IF NOT EXISTS idx_carteira_fundo ON carteira(fundo_cnpj);
CREATE INDEX IF NOT EXISTS idx_carteira_emissor ON carteira(emissor_cnpj);
CREATE INDEX IF NOT EXISTS idx_carteira_ligado ON carteira(emissor_ligado);
"""


def cnpjs_master(con: sqlite3.Connection) -> set[str]:
    rows = con.execute("""
        SELECT DISTINCT fundo_cnpj FROM papeis_fundo
        UNION SELECT cnpj FROM empresas
    """).fetchall()
    return {r[0] for r in rows if r[0] and len(r[0]) == 14}


def baixar_zip(ym: str) -> bytes | None:
    cache = CACHE_DIR / f"cda_fi_{ym}.zip"
    if cache.exists():
        return cache.read_bytes()
    url = URL_TEMPLATE.format(ym=ym)
    print(f"[CDA] baixando {url}")
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            print(f"[CDA] HTTP {r.status_code} para {ym}")
            return None
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(r.content)
        return r.content
    except requests.RequestException as e:
        print(f"[CDA] erro {ym}: {e}")
        return None


COLS_RENAME = {
    "CNPJ_FUNDO_CLASSE": "fundo_cnpj",
    "DT_COMPTC": "data_competencia",
    "TP_APLIC": "tipo_aplicacao",
    "TP_ATIVO": "tipo_ativo",
    "EMISSOR_LIGADO": "emissor_ligado",
    "EMISSOR": "emissor_nome",
    "CPF_CNPJ_EMISSOR": "emissor_cnpj",
    "CD_ATIVO": "cod_ativo",
    "DS_ATIVO": "desc_ativo",
    "QT_POS_FINAL": "qt_pos_final",
    "VL_MERC_POS_FINAL": "vl_merc_pos_final",
    "VL_AQUIS_NEGOC": "vl_aquisicao",
    "VL_VENDA_NEGOC": "vl_venda",
}


def normalizar_csv(df: pd.DataFrame, alvo: set[str], bloco_nome: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    col_cnpj = "CNPJ_FUNDO_CLASSE" if "CNPJ_FUNDO_CLASSE" in df.columns else "CNPJ_FUNDO"
    if col_cnpj not in df.columns:
        return pd.DataFrame()
    df = df.copy()
    df["__norm"] = df[col_cnpj].astype(str).str.replace(r"\D", "", regex=True)
    df = df[df["__norm"].isin(alvo)].copy()
    if df.empty:
        return df
    df[col_cnpj] = df["__norm"]
    if "CPF_CNPJ_EMISSOR" in df.columns:
        df["CPF_CNPJ_EMISSOR"] = df["CPF_CNPJ_EMISSOR"].astype(str).str.replace(r"\D", "", regex=True)
    df = df.drop(columns="__norm")
    df = df.rename(columns=COLS_RENAME)
    keep = [v for v in COLS_RENAME.values() if v in df.columns]
    df = df[keep].copy()
    df["bloco"] = bloco_nome
    for c in ("qt_pos_final", "vl_merc_pos_final", "vl_aquisicao", "vl_venda"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def processar_zip(zip_bytes: bytes, alvo: set[str]) -> pd.DataFrame:
    frames = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for nome in zf.namelist():
            if not nome.endswith(".csv"):
                continue
            with zf.open(nome) as f:
                try:
                    df = pd.read_csv(f, sep=";", encoding="latin-1", dtype=str,
                                     on_bad_lines="skip", low_memory=False)
                except Exception as e:
                    print(f"[CDA] erro lendo {nome}: {e}")
                    continue
            df_norm = normalizar_csv(df, alvo, nome.replace(".csv", ""))
            if not df_norm.empty:
                print(f"[CDA]   {nome}: {len(df_norm)} linhas alvo")
                frames.append(df_norm)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def inserir(con: sqlite3.Connection, df: pd.DataFrame):
    if df.empty:
        return 0
    df.to_sql("carteira", con, if_exists="append", index=False)
    return len(df)


def resumo(con: sqlite3.Connection):
    print("\n[CDA] === RESUMO ===")
    (total,) = con.execute("SELECT COUNT(*) FROM carteira").fetchone()
    print(f"  linhas totais: {total}")

    print("\n[CDA] linhas com emissor_ligado != 'N' ou nao-nulo:")
    rows = con.execute("""
        SELECT data_competencia, fundo_cnpj, emissor_ligado, emissor_nome,
               ROUND(vl_merc_pos_final, 2) AS vl
        FROM carteira
        WHERE COALESCE(emissor_ligado, '') NOT IN ('', 'N')
        ORDER BY data_competencia, fundo_cnpj
    """).fetchall()
    if not rows:
        print("  (nenhuma linha marcada como emissor ligado)")
    for r in rows[:40]:
        print(f"  {r[0]} | {r[1]} | ligado={r[2]:>3} | R$ {r[4]:>15} | {(r[3] or '')[:50]}")

    print("\n[CDA] top 15 emissores cujos titulos foram comprados pelos fundos Master:")
    rows = con.execute("""
        SELECT emissor_nome, COUNT(*) AS n,
               ROUND(SUM(vl_merc_pos_final), 2) AS vl_total
        FROM carteira
        WHERE emissor_nome IS NOT NULL AND emissor_nome != ''
        GROUP BY emissor_nome
        ORDER BY vl_total DESC
        LIMIT 15
    """).fetchall()
    for r in rows:
        print(f"  R$ {r[2] or 0:>18} | {r[1]:>4} pos | {(r[0] or '')[:65]}")


def main():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript(SCHEMA)
    con.execute("DELETE FROM carteira")
    con.commit()

    alvo = cnpjs_master(con)
    print(f"[CDA] {len(alvo)} CNPJs alvo (fundos + entidades Master)")

    total_inseridas = 0
    for ym in PERIODOS:
        zip_bytes = baixar_zip(ym)
        if not zip_bytes:
            continue
        df = processar_zip(zip_bytes, alvo)
        n = inserir(con, df)
        print(f"[CDA] {ym}: {n} linhas inseridas")
        total_inseridas += n
        con.commit()

    print(f"\n[CDA] total inserido: {total_inseridas}")
    resumo(con)
    con.close()


if __name__ == "__main__":
    main()
