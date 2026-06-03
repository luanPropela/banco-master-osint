import sqlite3
from pathlib import Path

import pandas as pd

DB = Path("data/master.db")
SAIDA = Path("data/csv")
ENCODING = "utf-8-sig"


def export_tabela(con: sqlite3.Connection, arq_nome: str, sql: str) -> Path:
    df = pd.read_sql(sql, con)
    arq = SAIDA / arq_nome
    df.to_csv(arq, index=False, encoding=ENCODING)
    print(f"  {arq_nome:55}  {len(df):>6} linhas  {arq.stat().st_size/1024:>7.1f} KB")
    return arq


def limpar_antigos():
    legados = [
        "empresas.csv", "pessoas.csv", "participacoes.csv", "papeis_fundo.csv",
        "inf_diario.csv", "carteira.csv", "cvm_processos.csv", "cvm_acusados.csv",
        "fraude_nodes.csv", "fraude_edges.csv",
        "view_participacoes.csv", "view_ranking_pessoas.csv",
        "view_papeis_fundo.csv", "view_carteira_emissor_ligado.csv",
        "view_resgates_atipicos.csv", "view_fraude_grafo.csv",
        "view_acusados_master.csv",
    ]
    for nome in legados:
        p = SAIDA / nome
        if p.exists():
            p.unlink()


def main():
    if not DB.exists():
        raise SystemExit(f"master.db nao encontrado em {DB.resolve()}. Rode 'python -m db' antes.")

    SAIDA.mkdir(parents=True, exist_ok=True)
    limpar_antigos()
    con = sqlite3.connect(DB)

    print("\nTABELAS BRUTAS (espelho 1:1 do master.db)\n" + "-" * 70)

    export_tabela(con, "01_empresas.csv",
                  "SELECT * FROM empresas ORDER BY razao_social")

    export_tabela(con, "02_pessoas.csv",
                  "SELECT * FROM pessoas ORDER BY nome")

    export_tabela(con, "03_participacoes_socio_empresa.csv",
                  "SELECT * FROM participacoes ORDER BY data_entrada")

    export_tabela(con, "04_papeis_fundo_cvm.csv",
                  "SELECT * FROM papeis_fundo ORDER BY fundo_cnpj, papel")

    try:
        export_tabela(con, "05_serie_diaria_fmp_fgts.csv",
                      "SELECT * FROM inf_diario ORDER BY fundo_cnpj, data")
    except pd.io.sql.DatabaseError:
        print("  05_serie_diaria_fmp_fgts.csv                            (sem dados)")

    try:
        export_tabela(con, "06_composicao_carteira_cvm_cda.csv",
                      "SELECT * FROM carteira ORDER BY data_competencia, fundo_cnpj")
    except pd.io.sql.DatabaseError:
        print("  06_composicao_carteira_cvm_cda.csv                       (sem dados)")

    try:
        export_tabela(con, "07_cvm_processos_sancionadores.csv",
                      "SELECT * FROM cvm_processos ORDER BY data_abertura DESC")
        export_tabela(con, "08_cvm_acusados_em_processos.csv",
                      "SELECT * FROM cvm_acusados ORDER BY data_situacao DESC")
    except pd.io.sql.DatabaseError:
        print("  07_cvm_processos / 08_cvm_acusados (sem dados)")

    try:
        export_tabela(con, "09_grafo_fraude_nodes.csv",
                      "SELECT * FROM fraude_nodes ORDER BY tipo, label")
        export_tabela(con, "10_grafo_fraude_edges.csv",
                      "SELECT * FROM fraude_edges ORDER BY source")
    except pd.io.sql.DatabaseError:
        print("  09 / 10_grafo_fraude (sem dados — rode importar_grafo_fraude.py)")

    print("\nVIEWS LEGIVEIS (com nomes em vez de IDs)\n" + "-" * 70)

    export_tabela(con, "view_socio_empresa_data_cargo.csv", """
        SELECT
            p.data_entrada                       AS data_entrada,
            COALESCE(s.nome, soc.razao_social)   AS socio,
            CASE WHEN p.socio_pessoa_id > 0 THEN 'PF' ELSE 'PJ' END AS tipo_socio,
            p.qualificacao                       AS cargo,
            e.razao_social                       AS empresa,
            e.cnpj                               AS cnpj_empresa,
            e.uf                                 AS uf_empresa
        FROM participacoes p
        JOIN empresas e ON e.cnpj = p.empresa_cnpj
        LEFT JOIN pessoas s ON s.id = p.socio_pessoa_id
        LEFT JOIN empresas soc ON soc.cnpj = p.socio_empresa_cnpj
        ORDER BY p.data_entrada
    """)

    export_tabela(con, "view_ranking_pessoas_por_num_empresas.csv", """
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

    export_tabela(con, "view_papeis_fundo_com_nomes.csv", """
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

    export_tabela(con, "view_carteira_emissor_ligado_KATCH_UPPER.csv", """
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
        export_tabela(con, "view_resgates_atipicos_fmp_fgts.csv", """
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
        print("  view_resgates_atipicos_fmp_fgts.csv  (inf_diario nao populada)")

    try:
        export_tabela(con, "view_grafo_fraude_legivel.csv", """
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
        print("  view_grafo_fraude_legivel.csv   (fraude tables vazias)")

    try:
        export_tabela(con, "view_pessoas_master_que_sao_acusadas_cvm.csv", """
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
        print("  view_pessoas_master_que_sao_acusadas_cvm.csv  (sem dados)")

    leiame = SAIDA / "00_LEIA-ME.txt"
    leiame.write_text(
        "DATASETS CSV - banco-master-osint\n"
        "==================================\n\n"
        "Cada CSV usa encoding UTF-8 com BOM (utf-8-sig).\n"
        "Abre direto no Excel, LibreOffice, Google Sheets ou pandas.\n\n"
        "TABELAS BRUTAS (espelho do master.db):\n"
        "  01_empresas.csv                            - 100+ empresas do perimetro\n"
        "  02_pessoas.csv                             - 100+ pessoas fisicas do QSA\n"
        "  03_participacoes_socio_empresa.csv         - quem e socio de qual empresa, com data e cargo\n"
        "  04_papeis_fundo_cvm.csv                    - admin/gestor/custodiante de 57 fundos\n"
        "  05_serie_diaria_fmp_fgts.csv               - 4 FMP-FGTS dia a dia (PL, cotistas, resgate)\n"
        "  06_composicao_carteira_cvm_cda.csv         - em quais ativos os fundos investiram\n"
        "  07_cvm_processos_sancionadores.csv         - processos administrativos sancionadores CVM\n"
        "  08_cvm_acusados_em_processos.csv           - nomes acusados em cada processo\n"
        "  09_grafo_fraude_nodes.csv                  - entidades da teia de fraude\n"
        "  10_grafo_fraude_edges.csv                  - relacoes da teia de fraude\n\n"
        "VIEWS LEGIVEIS (com nomes ao inves de IDs):\n"
        "  view_socio_empresa_data_cargo.csv          - quem-cargo-empresa-data, tudo legivel\n"
        "  view_ranking_pessoas_por_num_empresas.csv  - top pessoas por num. empresas\n"
        "  view_papeis_fundo_com_nomes.csv            - fundo-papel-prestador\n"
        "  view_carteira_emissor_ligado_KATCH_UPPER.csv  - achado inedito KATCH->UPPER\n"
        "  view_resgates_atipicos_fmp_fgts.csv        - resgates >= R$ 10 mil\n"
        "  view_grafo_fraude_legivel.csv              - grafo com labels (sem IDs)\n"
        "  view_pessoas_master_que_sao_acusadas_cvm.csv  - matches QSA Master x PAS-CVM\n\n"
        "REGERAR TUDO:  python exportar_csv.py\n"
    , encoding="utf-8")
    print(f"\nResumo salvo em {leiame}")

    con.close()
    print(f"\nDONE. Arquivos em {SAIDA.resolve()}")


if __name__ == "__main__":
    main()
