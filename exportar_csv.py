import sqlite3
from pathlib import Path

import pandas as pd

DB = Path("data/master.db")
SAIDA = Path("data/csv")
ENCODING = "utf-8-sig"


def export_tabela(con: sqlite3.Connection, nome: str, sql: str | None = None) -> Path:
    df = pd.read_sql(sql or f"SELECT * FROM {nome}", con)
    arq = SAIDA / f"{nome}.csv"
    df.to_csv(arq, index=False, encoding=ENCODING)
    print(f"  {nome:30}  {len(df):>6} linhas  {arq.stat().st_size/1024:>7.1f} KB")
    return arq


def main():
    if not DB.exists():
        raise SystemExit(f"master.db nao encontrado em {DB.resolve()}. Rode 'python -m db' antes.")

    SAIDA.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)

    print("\nTABELAS BRUTAS\n" + "-" * 60)
    tabelas_brutas = [
        "empresas", "pessoas", "participacoes", "papeis_fundo",
        "inf_diario", "carteira", "cvm_processos", "cvm_acusados",
        "fraude_nodes", "fraude_edges",
    ]
    for t in tabelas_brutas:
        try:
            export_tabela(con, t)
        except pd.io.sql.DatabaseError:
            print(f"  {t:30}  (nao existe — pule a coleta correspondente)")

    print("\nVIEWS LEGIVEIS (com nomes em vez de IDs)\n" + "-" * 60)

    export_tabela(con, "view_participacoes", """
        SELECT
            p.data_entrada                AS data_entrada,
            COALESCE(s.nome, soc.razao_social) AS socio,
            CASE WHEN p.socio_pessoa_id > 0 THEN 'PF' ELSE 'PJ' END AS tipo_socio,
            p.qualificacao                AS cargo,
            e.razao_social                AS empresa,
            e.cnpj                        AS cnpj_empresa,
            e.uf                          AS uf_empresa,
            p.fonte                       AS fonte
        FROM participacoes p
        JOIN empresas e ON e.cnpj = p.empresa_cnpj
        LEFT JOIN pessoas s ON s.id = p.socio_pessoa_id
        LEFT JOIN empresas soc ON soc.cnpj = p.socio_empresa_cnpj
        ORDER BY p.data_entrada
    """)

    export_tabela(con, "view_ranking_pessoas", """
        SELECT
            s.nome                                       AS nome,
            COUNT(DISTINCT p.empresa_cnpj)               AS n_empresas,
            GROUP_CONCAT(DISTINCT p.qualificacao)        AS cargos,
            GROUP_CONCAT(DISTINCT e.razao_social)        AS empresas,
            MIN(p.data_entrada)                          AS primeira_entrada,
            MAX(p.data_entrada)                          AS ultima_entrada,
            s.faixa_etaria                               AS faixa_etaria
        FROM participacoes p
        JOIN pessoas s ON s.id = p.socio_pessoa_id
        JOIN empresas e ON e.cnpj = p.empresa_cnpj
        GROUP BY s.nome
        ORDER BY n_empresas DESC, s.nome
    """)

    export_tabela(con, "view_papeis_fundo", """
        SELECT
            e.razao_social   AS fundo,
            e.cnpj           AS cnpj_fundo,
            pf.papel         AS papel,
            pf.prestador_nome AS prestador,
            pf.prestador_cnpj AS cnpj_prestador
        FROM papeis_fundo pf
        JOIN empresas e ON e.cnpj = pf.fundo_cnpj
        ORDER BY e.razao_social, pf.papel
    """)

    export_tabela(con, "view_carteira_emissor_ligado", """
        SELECT
            c.data_competencia,
            e.razao_social    AS fundo,
            c.fundo_cnpj,
            c.emissor_nome    AS emissor,
            c.emissor_cnpj,
            c.emissor_ligado,
            c.vl_merc_pos_final AS valor_brl,
            c.tipo_aplicacao,
            c.tipo_ativo
        FROM carteira c
        LEFT JOIN empresas e ON e.cnpj = c.fundo_cnpj
        WHERE c.emissor_nome IS NOT NULL
        ORDER BY c.data_competencia, c.vl_merc_pos_final DESC
    """)

    try:
        export_tabela(con, "view_resgates_atipicos", """
            SELECT
                i.data,
                e.razao_social     AS fundo,
                i.fundo_cnpj,
                i.resgate_dia      AS resgate_brl,
                i.captacao_dia     AS captacao_brl,
                i.cotistas,
                i.pl               AS pl_brl,
                i.valor_cota
            FROM inf_diario i
            LEFT JOIN empresas e ON e.cnpj = i.fundo_cnpj
            WHERE i.resgate_dia >= 10000
            ORDER BY i.resgate_dia DESC
        """)
    except pd.io.sql.DatabaseError:
        print("  view_resgates_atipicos      (inf_diario nao populada)")

    try:
        export_tabela(con, "view_fraude_grafo", """
            SELECT
                e.source                 AS de,
                ns.label                 AS de_label,
                ns.tipo                  AS de_tipo,
                e.target                 AS para,
                nt.label                 AS para_label,
                nt.tipo                  AS para_tipo,
                e.tipo                   AS tipo_relacao,
                e.detalhes               AS detalhes,
                e.fonte                  AS fonte
            FROM fraude_edges e
            JOIN fraude_nodes ns ON ns.node_id = e.source
            JOIN fraude_nodes nt ON nt.node_id = e.target
            ORDER BY e.source
        """)
    except pd.io.sql.DatabaseError:
        print("  view_fraude_grafo           (fraude_nodes/edges nao populadas)")

    try:
        export_tabela(con, "view_acusados_master", """
            SELECT
                s.nome           AS pessoa_no_dataset_master,
                a.nup            AS processo_nup,
                a.situacao       AS situacao_acusado,
                a.data_situacao,
                p.objeto         AS objeto_processo,
                p.data_abertura,
                p.fase_atual
            FROM cvm_acusados a
            JOIN pessoas s ON UPPER(a.nome_acusado) = UPPER(s.nome)
            LEFT JOIN cvm_processos p ON p.nup = a.nup
            ORDER BY a.data_situacao DESC
        """)
    except pd.io.sql.DatabaseError:
        print("  view_acusados_master        (cvm_acusados nao populada)")

    leiame = SAIDA / "LEIA-ME.txt"
    leiame.write_text(
        "DATASETS CSV - banco-master-osint\n"
        "==================================\n\n"
        "Cada CSV usa encoding UTF-8 com BOM (utf-8-sig).\n"
        "Abre direto no Excel, LibreOffice, Google Sheets, pandas.\n\n"
        "TABELAS BRUTAS (espelho do master.db):\n"
        "  empresas.csv         - 100 empresas (CNPJ, razao, UF, situacao)\n"
        "  pessoas.csv          - 104 pessoas fisicas (id, nome, faixa etaria)\n"
        "  participacoes.csv    - 164 ligacoes socio->empresa com IDs\n"
        "  papeis_fundo.csv     - 156 papeis CVM (admin/gestor/custodiante)\n"
        "  inf_diario.csv       - 517 dias dos 4 FMP-FGTS\n"
        "  carteira.csv         - composicao da carteira (CDA)\n"
        "  cvm_processos.csv    - 543 processos sancionadores CVM\n"
        "  cvm_acusados.csv     - 1934 acusados em PAS-CVM\n\n"
        "VIEWS LEGIVEIS (com nomes ao inves de IDs):\n"
        "  view_participacoes.csv             - quem-cargo-empresa-data\n"
        "  view_ranking_pessoas.csv           - top pessoas por num. empresas\n"
        "  view_papeis_fundo.csv              - fundo-papel-prestador\n"
        "  view_carteira_emissor_ligado.csv   - fundo-emissor-valor-flag ligado\n"
        "  view_resgates_atipicos.csv         - dias com resgate >= R$ 10 mil\n"
        "  view_acusados_master.csv           - matches do nosso QSA com PAS-CVM\n\n"
        "Para regenerar tudo: python exportar_csv.py\n"
    , encoding="utf-8")
    print(f"\nResumo salvo em {leiame}")

    con.close()
    print(f"\nDONE. Arquivos em {SAIDA.resolve()}")


if __name__ == "__main__":
    main()
