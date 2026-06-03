import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path("data/master.db")
CHANGELOG = Path.home() / "Downloads" / "banco-master-cvmweb-mudancas.csv"
FONTE = "CVMWeb consulta manual 03/06/2026"

ATUALIZA_CNPJ = {
    "FUNDO_SDG_II":      "46909301000133",
    "FUNDO_HANS_95":     "32088041000178",
    "FUNDO_ANNA":        "53273475000118",
    "FIDC_MARANTA":      "42584801000191",
    "FIDC_GOLD_STYLE":   "34081900000122",
    "FUNDO_TERMOPILAS":  "53311600000137",
    "FUNDO_ALUCARD":     "58807049000130",
    "CBSF_DTVM":         "34829992000186",
}

NODES_NOVOS = [
    ("CBSF_TRUST_ADM",  "CBSF Trust Administradora de Recursos Ltda", "Gestora",
     "23863529000134", "Gestor da carteira do SDG II FIDC (vinculada à CBSF/Reag)"),
    ("MARCOS_F_COSTA",  "Marcos Ferreira Costa", "Pessoa Física", None,
     "Diretor do SDG II FIDC; CPF parcial 296.447.968-29"),
    ("DIEGO_NASCIMENTO","Diego Peres da Costa Nascimento", "Pessoa Física", None,
     "Diretor responsável pela gestão do SDG II; CPF 111.681.947-33"),
]

EDGES_NOVAS = [
    ("CBSF_DTVM",        "FUNDO_SDG_II",     "ADMINISTRA",
     "CBSF DTVM (ex-Reag Trust) é a administradora do SDG II desde 15/09/2022"),
    ("CBSF_TRUST_ADM",   "FUNDO_SDG_II",     "GERE",
     "Gestor da carteira do SDG II"),
    ("MARCOS_F_COSTA",   "FUNDO_SDG_II",     "DIRETOR_DO_FUNDO",
     "Diretor responsável formal do fundo SDG II"),
    ("DIEGO_NASCIMENTO", "FUNDO_SDG_II",     "DIRETOR_DE_GESTAO",
     "Diretor responsável pela gestão da carteira"),
    ("REAG_INVEST",      "CBSF_TRUST_ADM",   "GRUPO",
     "CBSF Trust pertence ao grupo Reag (site www.reag.com.br)"),
    ("CBSF_DTVM",        "CBSF_TRUST_ADM",   "GRUPO",
     "Ambas com nome CBSF, mesma estrutura societária Reag"),
]


def main():
    if not DB.exists():
        raise SystemExit(f"master.db nao encontrado em {DB}")

    con = sqlite3.connect(DB)
    atualizados = []
    inseridos_nodes = []
    inseridas_edges = []
    erros = []

    for node_id, cnpj in ATUALIZA_CNPJ.items():
        cur = con.execute("UPDATE fraude_nodes SET cnpj = ? WHERE node_id = ? AND (cnpj IS NULL OR cnpj = '')", (cnpj, node_id))
        if cur.rowcount > 0:
            atualizados.append((node_id, cnpj))
        else:
            ja = con.execute("SELECT cnpj FROM fraude_nodes WHERE node_id = ?", (node_id,)).fetchone()
            if ja:
                erros.append((node_id, f"ja tinha cnpj={ja[0]}"))
            else:
                erros.append((node_id, "node nao existe"))

    for node_id, label, tipo, cnpj, descricao in NODES_NOVOS:
        ja = con.execute("SELECT 1 FROM fraude_nodes WHERE node_id = ?", (node_id,)).fetchone()
        if ja:
            erros.append((node_id, "node ja existe"))
            continue
        con.execute("""
            INSERT INTO fraude_nodes (node_id, label, tipo, descricao, cnpj, fonte)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (node_id, label, tipo, descricao, cnpj, FONTE))
        inseridos_nodes.append((node_id, label, cnpj))

    nodes_validos = {r[0] for r in con.execute("SELECT node_id FROM fraude_nodes").fetchall()}

    for source, target, tipo, detalhes in EDGES_NOVAS:
        if source not in nodes_validos or target not in nodes_validos:
            erros.append((f"{source}->{target}", "edge sem node"))
            continue
        ja = con.execute(
            "SELECT 1 FROM fraude_edges WHERE source = ? AND target = ? AND tipo = ?",
            (source, target, tipo)).fetchone()
        if ja:
            continue
        con.execute("""
            INSERT INTO fraude_edges (source, target, tipo, detalhes, fonte)
            VALUES (?, ?, ?, ?, ?)
        """, (source, target, tipo, detalhes, FONTE))
        inseridas_edges.append((source, target, tipo, detalhes))

    con.commit()
    (total_n,) = con.execute("SELECT COUNT(*) FROM fraude_nodes").fetchone()
    (total_e,) = con.execute("SELECT COUNT(*) FROM fraude_edges").fetchone()
    com_cnpj = con.execute("SELECT COUNT(*) FROM fraude_nodes WHERE cnpj IS NOT NULL").fetchone()[0]
    con.close()

    print(f"\n=== RESUMO ===")
    print(f"CNPJ atualizado em nodes:     {len(atualizados):>3}  ({', '.join(n for n,_ in atualizados)})")
    print(f"Nodes novos inseridos:        {len(inseridos_nodes):>3}")
    print(f"Edges novas inseridas:        {len(inseridas_edges):>3}")
    print(f"Erros/avisos:                 {len(erros):>3}  ({erros[:3]}...)")
    print(f"TOTAL agora:                  nodes={total_n}, edges={total_e}, nodes com CNPJ={com_cnpj}/{total_n}")

    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    import csv
    with CHANGELOG.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp","categoria","node_id_ou_source","target","label_ou_tipo","cnpj","detalhes"])
        for node_id, cnpj in atualizados:
            w.writerow([ts, "CNPJ ADICIONADO", node_id, "", "", cnpj, "via CVMWeb"])
        for node_id, label, cnpj in inseridos_nodes:
            w.writerow([ts, "NODE NOVO", node_id, "", label, cnpj or "", ""])
        for source, target, tipo, det in inseridas_edges:
            w.writerow([ts, "EDGE NOVA", source, target, tipo, "", det])
        for nid, msg in erros:
            w.writerow([ts, "AVISO", nid, "", "", "", msg])

    print(f"\nChangelog em {CHANGELOG}")


if __name__ == "__main__":
    main()
