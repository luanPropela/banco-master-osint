"""Exporta TODAS as tabelas do master.db para CSV (nomes descritivos) na pasta da investigação.
Garante que nada usado fique 'preso' só no SQLite."""
import os, sqlite3, csv

DBS = ["data/master.db", "coleta/data/master.db"]
OUT = "investigacao-claude/dados/master_db_export"
PREFIXO = {  # nome de tabela -> nome de arquivo descritivo
    "empresas": "empresas_perimetro",
    "pessoas": "pessoas_qsa",
    "participacoes": "participacoes_socio_empresa",
    "papeis_fundo": "papeis_admin_gestor_custodiante_cvm",
    "inf_diario": "informe_diario_fmp_fgts",
    "carteira": "carteira_cda_fi",
    "fraude_nodes": "grafo_fraude_nodes",
    "fraude_edges": "grafo_fraude_edges",
    "sancoes": "cvm_processos_sancionadores",
    "acusados": "cvm_acusados_em_processos",
}


def export_db(db, seen):
    if not os.path.exists(db):
        return
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    for t in tabs:
        if t in seen or t.startswith("sqlite_"):
            continue
        rows = con.execute(f'SELECT * FROM "{t}"').fetchall()
        nome = PREFIXO.get(t, t)
        path = f"{OUT}/{nome}.csv"
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            if rows:
                w.writerow(rows[0].keys())
                w.writerows([list(r) for r in rows])
            else:
                cols = [c[1] for c in con.execute(f'PRAGMA table_info("{t}")')]
                w.writerow(cols)
        print(f"  {db} :: {t:16} -> {nome}.csv ({len(rows)} linhas)")
        seen.add(t)
    con.close()


def main():
    os.makedirs(OUT, exist_ok=True)
    seen = set()
    for db in DBS:
        export_db(db, seen)
    print(f"\nTabelas exportadas: {len(seen)} -> {OUT}/")


if __name__ == "__main__":
    main()
