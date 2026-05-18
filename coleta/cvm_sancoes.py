import io
import sqlite3
import zipfile
from pathlib import Path

import pandas as pd
import requests

URL_PAS = "https://dados.cvm.gov.br/dados/PROCESSO/SANCIONADOR/DADOS/processo_sancionador.zip"
CACHE_ZIP = Path("data/cvm_sancao.zip")
DB_PATH = Path("data/master.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS cvm_processos (
    nup                  TEXT PRIMARY KEY,
    objeto               TEXT,
    ementa               TEXT,
    data_abertura        TEXT,
    fase_atual           TEXT,
    subfase_atual        TEXT,
    data_ultima_movim    TEXT
);
CREATE TABLE IF NOT EXISTS cvm_acusados (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nup             TEXT,
    nome_acusado    TEXT,
    situacao        TEXT,
    data_situacao   TEXT,
    UNIQUE (nup, nome_acusado, data_situacao)
);
CREATE INDEX IF NOT EXISTS idx_pas_acusado_nome ON cvm_acusados(nome_acusado);
"""


def baixar():
    if CACHE_ZIP.exists():
        return CACHE_ZIP.read_bytes()
    print(f"[PAS] baixando {URL_PAS}")
    r = requests.get(URL_PAS, timeout=60)
    r.raise_for_status()
    CACHE_ZIP.parent.mkdir(parents=True, exist_ok=True)
    CACHE_ZIP.write_bytes(r.content)
    return r.content


def carregar_csvs(zip_bytes: bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        with zf.open("processo_sancionador.csv") as f:
            df_proc = pd.read_csv(f, sep=";", encoding="latin-1", dtype=str, on_bad_lines="skip")
        with zf.open("processo_sancionador_acusado.csv") as f:
            df_acus = pd.read_csv(f, sep=";", encoding="latin-1", dtype=str, on_bad_lines="skip")
    return df_proc, df_acus


def inserir(con: sqlite3.Connection, df_proc: pd.DataFrame, df_acus: pd.DataFrame):
    con.executescript(SCHEMA)
    df_proc = df_proc.rename(columns={
        "NUP": "nup", "Objeto": "objeto", "Ementa": "ementa",
        "Data_Abertura": "data_abertura", "Fase_Atual": "fase_atual",
        "Subfase_Atual": "subfase_atual", "Data_Ultima_Movimentacao": "data_ultima_movim",
    })[["nup", "objeto", "ementa", "data_abertura", "fase_atual", "subfase_atual", "data_ultima_movim"]]
    df_acus = df_acus.rename(columns={
        "NUP": "nup", "Nome_Acusado": "nome_acusado",
        "Situacao": "situacao", "Data_Situacao": "data_situacao",
    })[["nup", "nome_acusado", "situacao", "data_situacao"]]

    con.execute("DELETE FROM cvm_processos")
    con.execute("DELETE FROM cvm_acusados")
    df_proc.to_sql("cvm_processos", con, if_exists="append", index=False)
    df_acus.to_sql("cvm_acusados", con, if_exists="append", index=False)
    con.commit()
    print(f"[PAS] {len(df_proc)} processos e {len(df_acus)} acusados inseridos")


def cruzar_com_dataset(con: sqlite3.Connection):
    print("\n[PAS] === ACUSADOS DA CVM QUE BATEM COM PESSOAS DO MASTER.DB ===")
    matches = pd.read_sql("""
        SELECT DISTINCT s.nome AS pessoa_master,
               a.nup, a.situacao, a.data_situacao,
               (SELECT objeto FROM cvm_processos p WHERE p.nup = a.nup) AS objeto
        FROM cvm_acusados a
        JOIN pessoas s ON UPPER(a.nome_acusado) = UPPER(s.nome)
        ORDER BY a.data_situacao DESC
    """, con)
    if matches.empty:
        print("  Nenhum acusado em processo sancionador CVM bateu com os 104 nomes do master.db.")
    else:
        for _, row in matches.iterrows():
            print(f"\n  >>> {row['pessoa_master']}")
            print(f"      NUP: {row['nup']}  |  {row['situacao']}  |  {row['data_situacao']}")
            print(f"      objeto: {(row['objeto'] or '')[:150]}")

    print("\n[PAS] === EMENTAS/OBJETOS QUE MENCIONAM RAZOES SOCIAIS DO MASTER.DB ===")
    razoes = [r[0] for r in con.execute("SELECT DISTINCT razao_social FROM empresas WHERE razao_social IS NOT NULL AND razao_social != ''").fetchall()]
    keywords = set()
    for r in razoes:
        if not r:
            continue
        primeira_palavra = r.upper().split()[0] if r.split() else ""
        if len(primeira_palavra) >= 4 and primeira_palavra not in {"BANCO", "FUNDO", "CAPITAL", "ASSET", "GESTORA", "INVESTIMENTOS", "PARTICIPACOES", "HOLDING", "ID", "S.A.", "LTDA"}:
            keywords.add(primeira_palavra)

    encontrados = 0
    for kw in sorted(keywords):
        rows = con.execute(
            "SELECT nup, data_abertura, objeto FROM cvm_processos WHERE UPPER(objeto) LIKE ? OR UPPER(ementa) LIKE ?",
            (f"%{kw}%", f"%{kw}%")
        ).fetchall()
        for nup, data, obj in rows:
            print(f"\n  >>> keyword '{kw}' encontrada em NUP {nup} ({data})")
            print(f"      {(obj or '')[:200]}")
            encontrados += 1
    if encontrados == 0:
        print("  Nenhuma menção encontrada.")


def main():
    zip_bytes = baixar()
    df_proc, df_acus = carregar_csvs(zip_bytes)
    con = sqlite3.connect(DB_PATH)
    inserir(con, df_proc, df_acus)
    cruzar_com_dataset(con)
    con.close()


if __name__ == "__main__":
    main()
