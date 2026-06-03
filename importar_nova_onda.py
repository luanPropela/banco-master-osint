import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path("data/master.db")
CHANGELOG_PATH = Path.home() / "Downloads" / "banco-master-mudancas.csv"

FONTE = "G1+CNN+ICL+Agência Brasil+Metropoles 27-28/05/2026 + Reag/CBSF 15/01/2026"

NODES_NOVOS = [
    ("CLAUDIO_CASTRO",       "Cláudio Castro",                  "Pessoa Física",           None,
     "Ex-governador RJ; encontros sincrônicos com aportes RioPrev → Master"),
    ("RICARDO_SIQUEIRA",     "Ricardo Siqueira Rodrigues",      "Pessoa Física",           None,
     "Lobista, ex-delator Lava Jato, elo Castro-Vorcaro; dono Mídias Promotora"),
    ("DEIVIS_ANTUNES",       "Deivis Marcon Antunes",           "Pessoa Física",           None,
     "Ex-presidente RioPrev jul/2023 a jan/2026; preso 03/02/2026 (2ª fase Compliance Zero)"),
    ("ANDRE_MENDONCA",       "Min. André Mendonça",             "Pessoa Física",           None,
     "STF; autorizou 8ª fase Compliance Zero em 27/05/2026"),
    ("GILSON_VASCONCELOS",   "Gilson Bahia Vasconcelos",        "Pessoa Física",           None,
     "Sócio aparente (laranja) da Mídias Promotora"),
    ("JOAO_MANSUR",          "João Carlos Mansur",              "Pessoa Física",           None,
     "Fundador Reag (2012); alvo da Operação Carbono Oculto"),
    ("FABIANO_ZETTEL",       "Fabiano Zettel",                  "Pessoa Física",           None,
     "Diretor Super Empreendimentos 2021-2024"),
    ("BETO_LOCO",            "Roberto Augusto Leme da Silva (Beto Loco)", "Pessoa Física", None,
     "Aster Petróleo; Carbono Oculto PCC"),
    ("MOHAMAD_MOURAD",       "Mohamad Hussein Mourad",          "Pessoa Física",           None,
     "Aster e Copape; PCC"),

    ("RIOPREVIDENCIA",       "RioPrevidência",                  "Órgão Público RPPS",      "03066219000181",
     "Autarquia RJ; 235k servidores; R$ 3,69 bi para Master"),
    ("MIDIAS_PROMOTORA",     "Mídias Promotora Ltda",           "Empresa",                 None,
     "R$ 126 mi do Master 2022-2025; sócio aparente Gilson Vasconcelos (laranja)"),
    ("REAG_INVEST",          "Reag Investimentos",              "Gestora",                 None,
     "Faria Lima; fundada 2012 por Mansur; ativos cresceram 14x (R$ 25 bi a R$ 341 bi 2020-2025)"),
    ("CBSF_DTVM",            "CBSF DTVM (ex-Reag Trust)",       "DTVM",                    None,
     "Liquidada 15/01/2026; alameda Gabriel Monteiro da Silva"),
    ("FIDC_GOLD_STYLE",      "Fundo Gold Style FIDC",           "Fundo de Investimento",   None,
     "Administrado pela Reag; recebeu R$ 1 bi de empresas PCC (Aster, BK Bank, Inovanti)"),
    ("FIDC_MARANTA",         "FIDC Maranta",                    "Fundo de Investimento",   None,
     "97% do portfólio em CCBs Lormont R$ 73,7 mi (Tanure)"),
    ("FUNDO_TERMOPILAS",     "Fundo Termópilas",                "Fundo de Investimento",   None,
     "Administrado por Reag; principal acionista da Super Empreendimentos"),
    ("FUNDO_ALUCARD",        "Alucard/Abbiamo FIP Multiestratégia", "Fundo de Investimento", None,
     "Administrado por Reag; controla Allora, Lenore, Milano, Stanza, Domani, Chesapeake"),

    ("BANCO_VOITER",         "Banco Voiter S.A. (ex-Indusval)", "Instituição Financeira",  "61024352000171",
     "Antigo nome de Banco Pleno; foi Indusval até 2020; integrou conglomerado Master em início 2024"),
    ("BANCO_PLENO",          "Banco Pleno S.A.",                "Instituição Financeira",  "61024352000171",
     "Ex-Voiter; controle Augusto Lima jul/2025; liquidado 18/02/2026"),
    ("BANCO_MAXIMA",         "Banco Máxima (precursor histórico)", "Instituição Financeira", None,
     "Forma anterior do Banco Master S.A."),

    ("ASTER_PETROLEO",       "Aster Petróleo LTDA.",            "Empresa",                 "02377759000113",
     "Carbono Oculto PCC; R$ 759,5 mi para Gold Style; controla HD em PI"),
    ("BK_BANK",              "BK Bank (Instituição de Pagamento)", "Fintech/IP",           None,
     "Banco-sombra do PCC; R$ 9 bi 2020-2024; R$ 158 mi para Gold Style"),
    ("INOVANTI",             "Inovanti Instituição de Pagamento", "Fintech/IP",            None,
     "Carbono Oculto; R$ 175 mi para Gold Style; R$ 778 mi totais movimentados"),
    ("HD_PETROLEO",          "HD Petróleo (postos PI)",         "Empresa",                 "21228180000133",
     "Rede de postos em Teresina/PI controlada pela Aster"),
    ("COPAPE",               "Copape Produtos de Petróleo",     "Empresa",                 None,
     "Fornece combustíveis para Aster; PCC"),

    ("TRUMP_HOTEL_BARRA",    "Antigo Trump Hotel Barra/RJ",     "Empresa",                 None,
     "Vítima de fraude R$ 17 mi por Ricardo Siqueira"),
    ("PLANNER",              "Planner Corretora",               "Corretora",               None,
     "Mauricio Quadrado foi sócio até 2022"),
    ("TIRRENO",              "Tirreno (empresa-fachada)",       "Empresa",                 None,
     "Fachada do Vorcaro; R$ 12,2 bi em carteiras fictícias para BRB"),
    ("BRB",                  "Banco de Brasília",               "Instituição Financeira",  None,
     "Comprou R$ 12 bi em carteiras Master via Tirreno; venda do Master bloqueada BACEN 17/11/2025"),
    ("FICTOR",               "Fictor Holding Financeira",       "Holding",                 None,
     "Consórcio comprador frustrado do Master; sob investigação"),

    ("OP_CARBONO_OCULTO",    "Operação Carbono Oculto",         "Operação Policial",       None,
     "PF; investiga lavagem PCC no sistema financeiro; deflagrada 28/08/2025"),
    ("POLICIA_FEDERAL",      "Polícia Federal",                 "Órgão Regulador",         None,
     "Conduz Operação Compliance Zero (8 fases) e Carbono Oculto"),
    ("STF",                  "Supremo Tribunal Federal",        "Órgão Regulador",         None,
     "Autoriza fases das operações (Min. André Mendonça relator)"),
]

EDGES_NOVAS = [
    ("CLAUDIO_CASTRO",     "DANIEL_VORCARO",     "ENCONTROS_PRIVADOS",     "Encontros frequentes priv. e exterior; Vorcaro pagava as despesas (PF)"),
    ("RIOPREVIDENCIA",     "BANCO_MASTER",       "APORTE_FINANCEIRO",      "R$ 3,69 bi total entre 2023-2024 (LFs + fundos)"),
    ("RIOPREVIDENCIA",     "BANCO_MASTER",       "APORTE_LF_SINCRONO",     "R$ 80 mi em 15/05/2024 (24h após encontro Castro-Vorcaro em NY)"),
    ("RIOPREVIDENCIA",     "BANCO_MASTER",       "APORTE_LFS_PERIODO",     "R$ 960 mi em LFs entre out/2023 e ago/2024 (venc. 2033-2034)"),
    ("RIOPREVIDENCIA",     "BANCO_MASTER",       "APORTE_7_DEPOSITOS",     "7 depósitos entre nov/2023 e jul/2024 somando R$ 970 mi"),

    ("DEIVIS_ANTUNES",     "RIOPREVIDENCIA",     "PRESIDIU",               "05/07/2023 a jan/2026; renúncia em meio à investigação"),
    ("DEIVIS_ANTUNES",     "POLICIA_FEDERAL",    "PRESO_POR",              "03/02/2026 (2ª fase Compliance Zero)"),

    ("RICARDO_SIQUEIRA",   "CLAUDIO_CASTRO",     "INTERMEDIOU",            "Aproximou banqueiro do governador (PF)"),
    ("RICARDO_SIQUEIRA",   "DANIEL_VORCARO",     "INTERMEDIOU",            "Articulador, capturer e lobbyist; identificava oportunidades"),
    ("RICARDO_SIQUEIRA",   "MIDIAS_PROMOTORA",   "OPERA_LARANJA",          "Empresa registrada em nome de testa-de-ferro (Gilson Vasconcelos)"),
    ("RICARDO_SIQUEIRA",   "TRUMP_HOTEL_BARRA",  "FRAUDOU",                "R$ 17 mi (caso anterior)"),
    ("GILSON_VASCONCELOS", "MIDIAS_PROMOTORA",   "SOCIO_LARANJA",          "Único sócio aparente; beneficiário do auxílio emergencial pandemia"),
    ("BANCO_MASTER",       "MIDIAS_PROMOTORA",   "PAGAMENTO",              "R$ 126 mi transferidos entre 2022 e 2025"),
    ("ANDRE_MENDONCA",     "POLICIA_FEDERAL",    "AUTORIZOU",              "Decisão STF 27/05/2026 — 8ª fase Compliance Zero"),

    ("JOAO_MANSUR",        "REAG_INVEST",        "FUNDADOR",               "Fundou em 2012"),
    ("JOAO_MANSUR",        "CBSF_DTVM",          "CONTROLADOR",            "Antiga Reag Trust DTVM"),
    ("REAG_INVEST",        "CBSF_DTVM",          "GRUPO",                  "Liquidada 15/01/2026 pelo BACEN"),
    ("REAG_INVEST",        "FIDC_GOLD_STYLE",    "ADMINISTRA",             "Recebeu R$ 1 bi de empresas PCC"),
    ("REAG_INVEST",        "FUNDO_TERMOPILAS",   "ADMINISTRA",             None),
    ("REAG_INVEST",        "FUNDO_ALUCARD",      "ADMINISTRA",             "Controla Allora, Lenore, Milano, Stanza, Domani, Chesapeake"),
    ("REAG_INVEST",        "FUNDO_HANS_95",      "ADMINISTRA",             "Hans 95 pertence à Reag (ICL)"),
    ("FUNDO_TERMOPILAS",   "SUPER_EMPREENDIMENTOS", "PRINCIPAL_ACIONISTA", "Termópilas é o principal acionista da Super (R$ 2,6 bi de capital)"),
    ("FABIANO_ZETTEL",     "SUPER_EMPREENDIMENTOS", "DIRETOR",             "Diretor entre ago/2021 e jul/2024"),

    ("ASTER_PETROLEO",     "FIDC_GOLD_STYLE",    "APORTOU",                "R$ 759,5 mi para o Gold Style"),
    ("BK_BANK",            "FIDC_GOLD_STYLE",    "APORTOU",                "R$ 158 mi"),
    ("INOVANTI",           "FIDC_GOLD_STYLE",    "APORTOU",                "R$ 175 mi"),
    ("ASTER_PETROLEO",     "HD_PETROLEO",        "CONTROLA",               "Rede de postos em Teresina/PI"),
    ("ASTER_PETROLEO",     "COPAPE",             "COMERCIALIZA",           "Combustíveis fabricados pela Copape"),
    ("BETO_LOCO",          "ASTER_PETROLEO",     "LIGADO_A",               None),
    ("MOHAMAD_MOURAD",     "ASTER_PETROLEO",     "LIGADO_A",               None),
    ("MOHAMAD_MOURAD",     "COPAPE",             "LIGADO_A",               None),

    ("NELSON_TANURE",      "FIDC_MARANTA",       "BENEFICIARIO_FINAL",     "Via Lormont; CCBs R$ 73,7 mi = 97% do portfólio"),
    ("FIDC_MARANTA",       "LORMONT_PART",       "TEM_CCB",                "R$ 73,7 mi em CCBs Lormont (97% do portfólio)"),
    ("LORMONT_PART",       "REAG_INVEST",        "FLUXO_R720MI",           "Empréstimos para Reag R$ 720 mi (Carbono Oculto)"),

    ("MAURICIO_QUADRADO",  "PLANNER",            "EX_SOCIO",               "Sócio até 2022, quando criou Trustee DTVM"),
    ("BANVOX",             "DANIEL_VORCARO",     "COFUNDADO_POR",          "Vorcaro e Quadrado criaram em 2020"),
    ("BANVOX",             "MAURICIO_QUADRADO",  "COFUNDADO_POR",          "Idem"),

    ("AUGUSTO_LIMA",       "BANCO_VOITER",       "ADQUIRIU",               "07/2025 — após sair Master em 05/2024"),
    ("BANCO_VOITER",       "BANCO_PLENO",        "RENOMEACAO",             "Mesmo CNPJ 61.024.352/0001-71"),
    ("BANCO_PLENO",        "POLICIA_FEDERAL",    "LIQUIDADO",              "18/02/2026 pelo BACEN"),
    ("DANIEL_VORCARO",     "BANCO_VOITER",       "PARTICIPOU",             "Indusval/Voiter integrado ao conglomerado Master início 2024"),

    ("BANCO_MAXIMA",       "BANCO_MASTER",       "TRANSFORMOU_EM",         "Banco Máxima virou Banco Master S.A."),
    ("DANIEL_VORCARO",     "TIRRENO",            "CONTROLA_FACHADA",       "Empresa de fachada criada por Vorcaro (PF)"),
    ("BANCO_MASTER",       "TIRRENO",            "VENDEU_CARTEIRAS",       "Para Tirreno; depois vendidas pra BRB"),
    ("TIRRENO",            "BRB",                "VENDEU_CARTEIRAS",       "R$ 12,2 bi em carteiras fictícias (PF: contratos fabricados)"),
    ("FICTOR",             "BANCO_MASTER",       "COMPRA_ANUNCIADA",       "Mar/2025; BACEN bloqueou em 17/11/2025"),
    ("BACEN",              "FICTOR",             "BLOQUEOU_COMPRA",        "17/11/2025"),

    ("OP_CARBONO_OCULTO",  "REAG_INVEST",        "INVESTIGA",              "Lavagem PCC; deflagrada 28/08/2025"),
    ("OP_CARBONO_OCULTO",  "TRUSTEE_DTVM",       "INVESTIGA",              "Lavagem PCC"),
    ("OP_CARBONO_OCULTO",  "BANVOX",             "INVESTIGA",              "Banvox DTVM também acusada"),
    ("OP_CARBONO_OCULTO",  "ASTER_PETROLEO",     "INVESTIGA",              "PCC combustíveis"),
    ("OP_CARBONO_OCULTO",  "BK_BANK",            "INVESTIGA",              "PCC fintech"),
    ("OP_CARBONO_OCULTO",  "INOVANTI",          "INVESTIGA",              "PCC fintech"),
]


def main():
    if not DB.exists():
        raise SystemExit(f"master.db nao encontrado em {DB}. Rode 'python -m db' primeiro.")

    con = sqlite3.connect(DB)

    inseridos_nodes = []
    ja_existem_nodes = []
    inseridas_edges = []
    ignoradas_edges = []

    for node_id, label, tipo, descricao, cnpj in [(n[0], n[1], n[2], n[4], n[3]) for n in NODES_NOVOS]:
        ja = con.execute("SELECT 1 FROM fraude_nodes WHERE node_id = ?", (node_id,)).fetchone()
        if ja:
            ja_existem_nodes.append(node_id)
            continue
        con.execute("""
            INSERT INTO fraude_nodes (node_id, label, tipo, descricao, cnpj, fonte)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (node_id, label, tipo, descricao, cnpj, FONTE))
        inseridos_nodes.append((node_id, label, tipo, cnpj, descricao))

    nodes_validos = {r[0] for r in con.execute("SELECT node_id FROM fraude_nodes").fetchall()}

    for source, target, tipo, detalhes in EDGES_NOVAS:
        if source not in nodes_validos or target not in nodes_validos:
            ignoradas_edges.append((source, target, tipo, "node ausente"))
            continue
        ja = con.execute(
            "SELECT 1 FROM fraude_edges WHERE source = ? AND target = ? AND tipo = ?",
            (source, target, tipo)
        ).fetchone()
        if ja:
            ignoradas_edges.append((source, target, tipo, "ja existe"))
            continue
        con.execute("""
            INSERT INTO fraude_edges (source, target, tipo, detalhes, fonte)
            VALUES (?, ?, ?, ?, ?)
        """, (source, target, tipo, detalhes, FONTE))
        inseridas_edges.append((source, target, tipo, detalhes))

    con.commit()

    (total_n,) = con.execute("SELECT COUNT(*) FROM fraude_nodes").fetchone()
    (total_e,) = con.execute("SELECT COUNT(*) FROM fraude_edges").fetchone()
    con.close()

    print(f"\n=== RESUMO ===")
    print(f"nodes inseridos:    {len(inseridos_nodes):>3}")
    print(f"nodes ja existiam:  {len(ja_existem_nodes):>3}  ({', '.join(ja_existem_nodes) or '-'})")
    print(f"edges inseridas:    {len(inseridas_edges):>3}")
    print(f"edges ignoradas:    {len(ignoradas_edges):>3}  ({len([e for e in ignoradas_edges if e[3] == 'ja existe'])} duplicadas, {len([e for e in ignoradas_edges if e[3] == 'node ausente'])} sem node)")
    print(f"TOTAL agora:        nodes={total_n}  edges={total_e}")

    CHANGELOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with CHANGELOG_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        import csv
        w = csv.writer(f)
        w.writerow(["timestamp", "categoria", "node_id_ou_source", "target", "tipo_ou_label", "cnpj", "detalhes_ou_descricao"])
        for node_id, label, tipo, cnpj, descricao in inseridos_nodes:
            w.writerow([ts, "NODE INSERIDO", node_id, "", f"{tipo}: {label}", cnpj or "", descricao])
        for source, target, tipo, detalhes in inseridas_edges:
            w.writerow([ts, "EDGE INSERIDA", source, target, tipo, "", detalhes or ""])
        for node_id in ja_existem_nodes:
            w.writerow([ts, "NODE JA EXISTIA", node_id, "", "", "", ""])
        for source, target, tipo, motivo in ignoradas_edges:
            w.writerow([ts, "EDGE IGNORADA", source, target, tipo, "", motivo])

    print(f"\n=== CHANGELOG salvo em (NAO commitado) ===")
    print(f"  {CHANGELOG_PATH}")


if __name__ == "__main__":
    main()
