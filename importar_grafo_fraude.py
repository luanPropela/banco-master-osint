import sqlite3
from pathlib import Path

import pandas as pd

DB = Path("data/master.db")
XLSX = Path(r"C:\Users\carly\OneDrive\Pictures\Camera Roll\dados_grafo_banco_master.xlsx")

SCHEMA = """
CREATE TABLE IF NOT EXISTS fraude_nodes (
    node_id     TEXT PRIMARY KEY,
    label       TEXT,
    tipo        TEXT,
    descricao   TEXT,
    cnpj        TEXT,
    fonte       TEXT DEFAULT 'ICL/Folha 2026-05-28'
);
CREATE TABLE IF NOT EXISTS fraude_edges (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    source      TEXT NOT NULL,
    target      TEXT NOT NULL,
    tipo        TEXT,
    detalhes    TEXT,
    fonte       TEXT DEFAULT 'ICL/Folha 2026-05-28',
    FOREIGN KEY (source) REFERENCES fraude_nodes(node_id),
    FOREIGN KEY (target) REFERENCES fraude_nodes(node_id)
);
CREATE INDEX IF NOT EXISTS idx_fraude_edges_source ON fraude_edges(source);
CREATE INDEX IF NOT EXISTS idx_fraude_edges_target ON fraude_edges(target);
"""

NODE_TO_CNPJ = {
    "BANCO_MASTER":           "33923798000100",
    "VIKING":                 "07875796000175",
    "FUNDO_LANCIA":           "29786909000107",
    "DV_HOLDING":             "57445179000108",
    "SUPER_EMPREENDIMENTOS":  "31446245000170",
    "LORMONT_PART":           "34263138000103",
    "BANVOX":                 "38461854000148",
}


def main():
    if not XLSX.exists():
        raise SystemExit(f"Excel nao encontrado em {XLSX}")
    if not DB.exists():
        raise SystemExit(f"master.db nao encontrado em {DB}. Rode 'python -m db' primeiro.")

    nodes_df = pd.read_excel(XLSX, sheet_name="Nodes")
    edges_df = pd.read_excel(XLSX, sheet_name="Edges")
    print(f"Excel: {len(nodes_df)} nodes, {len(edges_df)} edges")

    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    con.execute("DELETE FROM fraude_edges")
    con.execute("DELETE FROM fraude_nodes")

    for _, row in nodes_df.iterrows():
        nid = row["ID"]
        con.execute("""
            INSERT INTO fraude_nodes (node_id, label, tipo, descricao, cnpj)
            VALUES (?, ?, ?, ?, ?)
        """, (nid, row["Label"], row["Type"], row["Description"], NODE_TO_CNPJ.get(nid)))

    for _, row in edges_df.iterrows():
        con.execute("""
            INSERT INTO fraude_edges (source, target, tipo, detalhes)
            VALUES (?, ?, ?, ?)
        """, (row["Source"], row["Target"], row["Type"], row["Details"]))

    con.commit()

    print(f"\nNODES IMPORTADOS POR TIPO:")
    for r in con.execute("SELECT tipo, COUNT(*) FROM fraude_nodes GROUP BY tipo ORDER BY 2 DESC"):
        print(f"  {r[0]:30}  {r[1]}")

    print(f"\nEDGES IMPORTADAS POR TIPO:")
    for r in con.execute("SELECT tipo, COUNT(*) FROM fraude_edges GROUP BY tipo ORDER BY 2 DESC"):
        print(f"  {r[0]:25}  {r[1]}")

    print(f"\nNODES COM CNPJ CONFIRMADO (ja podem cruzar com 'empresas'):")
    rows = con.execute("""
        SELECT n.node_id, n.label, n.cnpj,
               (SELECT razao_social FROM empresas WHERE empresas.cnpj = n.cnpj) AS razao_db
        FROM fraude_nodes n
        WHERE n.cnpj IS NOT NULL
        ORDER BY n.label
    """).fetchall()
    for r in rows:
        marca = "(no master.db)" if r[3] else "(ainda nao no master.db)"
        print(f"  {r[2]}  {r[1]:35}  {marca}")

    print(f"\nNODES SEM CNPJ (FIDCs restritos + pessoas + reguladores):")
    for r in con.execute("SELECT node_id, label, tipo FROM fraude_nodes WHERE cnpj IS NULL ORDER BY tipo, label"):
        print(f"  {r[0]:25}  {r[1]:30}  [{r[2]}]")

    con.close()
    print(f"\nOK. Tabelas fraude_nodes e fraude_edges populadas em {DB}")


if __name__ == "__main__":
    main()
