import sqlite3
from pathlib import Path

import pandas as pd

DB = Path("data/master.db")
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_colwidth", 80)


def _con() -> sqlite3.Connection:
    return sqlite3.connect(DB)


def _q(sql: str, params: tuple = ()) -> pd.DataFrame:
    return pd.read_sql(sql, _con(), params=params)


def _like(termo: str) -> str:
    return f"%{termo.upper()}%"


def resumo() -> pd.DataFrame:
    linhas = []
    for tabela in ("empresas", "pessoas", "participacoes", "papeis_fundo", "inf_diario"):
        try:
            (n,) = _con().execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()
            linhas.append({"tabela": tabela, "linhas": n})
        except sqlite3.OperationalError:
            linhas.append({"tabela": tabela, "linhas": None})
    return pd.DataFrame(linhas)


def cobertura_empresas() -> pd.DataFrame:
    df = _q("SELECT * FROM empresas")
    return pd.DataFrame({
        "campo": df.columns,
        "preenchidos": [df[c].astype(str).replace("", pd.NA).notna().sum() for c in df.columns],
        "total": len(df),
    })


def empresas(fonte: str | None = None) -> pd.DataFrame:
    if fonte:
        return _q("SELECT * FROM empresas WHERE fonte = ? ORDER BY razao_social", (fonte,))
    return _q("SELECT * FROM empresas ORDER BY razao_social")


def empresa(termo: str) -> pd.DataFrame:
    if termo.isdigit():
        return _q("SELECT * FROM empresas WHERE cnpj = ?", (termo,))
    return _q(
        "SELECT * FROM empresas WHERE UPPER(razao_social) LIKE ? ORDER BY razao_social",
        (_like(termo),),
    )


def empresas_por_uf() -> pd.DataFrame:
    return _q("""
        SELECT COALESCE(NULLIF(uf, ''), '(nao informado)') AS uf, COUNT(*) AS n
        FROM empresas GROUP BY uf ORDER BY n DESC
    """)


def empresas_por_situacao() -> pd.DataFrame:
    return _q("""
        SELECT COALESCE(NULLIF(situacao, ''), '(nao informado)') AS situacao, COUNT(*) AS n
        FROM empresas GROUP BY situacao ORDER BY n DESC
    """)


def pessoas() -> pd.DataFrame:
    return _q("SELECT * FROM pessoas ORDER BY nome")


def pessoa(termo: str) -> pd.DataFrame:
    return _q(
        "SELECT * FROM pessoas WHERE UPPER(nome) LIKE ? ORDER BY nome",
        (_like(termo),),
    )


def ranking_pessoas(limite: int = 20) -> pd.DataFrame:
    return _q("""
        SELECT s.nome,
               COUNT(*) AS n_empresas,
               GROUP_CONCAT(p.qualificacao, ' | ') AS qualificacoes
        FROM participacoes p
        JOIN pessoas s ON s.id = p.socio_pessoa_id
        GROUP BY s.nome
        ORDER BY n_empresas DESC
        LIMIT ?
    """, (limite,))


def pessoas_em_n(n: int = 3) -> pd.DataFrame:
    return _q("""
        SELECT s.nome, COUNT(*) AS n_empresas
        FROM participacoes p
        JOIN pessoas s ON s.id = p.socio_pessoa_id
        GROUP BY s.nome
        HAVING n_empresas >= ?
        ORDER BY n_empresas DESC
    """, (n,))


def participacoes_de(nome: str) -> pd.DataFrame:
    return _q("""
        SELECT e.razao_social,
               p.qualificacao,
               p.data_entrada,
               e.situacao,
               e.uf
        FROM participacoes p
        JOIN pessoas s   ON s.id = p.socio_pessoa_id
        JOIN empresas e  ON e.cnpj = p.empresa_cnpj
        WHERE UPPER(s.nome) LIKE ?
        ORDER BY e.razao_social
    """, (_like(nome),))


def socios_da(termo: str) -> pd.DataFrame:
    if termo.isdigit():
        cond = "p.empresa_cnpj = ?"
        param = termo
    else:
        cond = "UPPER(e.razao_social) LIKE ?"
        param = _like(termo)
    return _q(f"""
        SELECT e.razao_social        AS empresa,
               COALESCE(s.nome, soc.razao_social) AS socio,
               CASE WHEN p.socio_pessoa_id > 0 THEN 'PF' ELSE 'PJ' END AS tipo,
               p.qualificacao,
               p.data_entrada
        FROM participacoes p
        JOIN empresas e ON e.cnpj = p.empresa_cnpj
        LEFT JOIN pessoas s ON s.id = p.socio_pessoa_id
        LEFT JOIN empresas soc ON soc.cnpj = p.socio_empresa_cnpj
        WHERE {cond}
        ORDER BY tipo, socio
    """, (param,))


def qualificacoes() -> pd.DataFrame:
    return _q("""
        SELECT qualificacao, COUNT(*) AS n
        FROM participacoes
        GROUP BY qualificacao
        ORDER BY n DESC
    """)


def fundos(termo: str | None = None) -> pd.DataFrame:
    base = """
        SELECT cnpj, razao_social, situacao
        FROM empresas
        WHERE fonte IN ('cvm', 'cvm_papel') AND cnae = 'FUNDO DE INVESTIMENTO'
    """
    if termo:
        return _q(base + " AND UPPER(razao_social) LIKE ? ORDER BY razao_social",
                  (_like(termo),))
    return _q(base + " ORDER BY razao_social")


def papeis_da(termo: str) -> pd.DataFrame:
    if termo.isdigit():
        cond = "pf.prestador_cnpj = ?"
        param = termo
    else:
        cond = "UPPER(pf.prestador_nome) LIKE ?"
        param = _like(termo)
    return _q(f"""
        SELECT e.razao_social AS fundo,
               pf.papel,
               e.situacao
        FROM papeis_fundo pf
        JOIN empresas e ON e.cnpj = pf.fundo_cnpj
        WHERE {cond}
        ORDER BY pf.papel, e.razao_social
    """, (param,))


def fundos_com_admin(cnpj_admin: str) -> pd.DataFrame:
    return _q("""
        SELECT e.razao_social AS fundo, e.situacao
        FROM papeis_fundo pf
        JOIN empresas e ON e.cnpj = pf.fundo_cnpj
        WHERE pf.papel = 'admin' AND pf.prestador_cnpj = ?
        ORDER BY e.razao_social
    """, (cnpj_admin,))


def gestoras_top(limite: int = 15) -> pd.DataFrame:
    return _q("""
        SELECT prestador_nome AS gestora, COUNT(*) AS n_fundos
        FROM papeis_fundo
        WHERE papel = 'gestor' AND prestador_nome IS NOT NULL
        GROUP BY prestador_nome
        ORDER BY n_fundos DESC
        LIMIT ?
    """, (limite,))


def custodiantes_top(limite: int = 15) -> pd.DataFrame:
    return _q("""
        SELECT prestador_nome AS custodiante, COUNT(*) AS n_fundos
        FROM papeis_fundo
        WHERE papel = 'custodiante' AND prestador_nome IS NOT NULL
        GROUP BY prestador_nome
        ORDER BY n_fundos DESC
        LIMIT ?
    """, (limite,))


def inf_diario_fundo(cnpj: str) -> pd.DataFrame:
    df = _q("""
        SELECT data, pl, valor_cota, captacao_dia, resgate_dia, cotistas
        FROM inf_diario
        WHERE fundo_cnpj = ?
        ORDER BY data
    """, (cnpj,))
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


def comparar_fundos(cnpjs: list[str]) -> pd.DataFrame:
    placeholders = ",".join("?" * len(cnpjs))
    df = _q(f"""
        SELECT i.fundo_cnpj, e.razao_social AS fundo, i.data,
               i.pl, i.cotistas, i.captacao_dia, i.resgate_dia
        FROM inf_diario i
        LEFT JOIN empresas e ON e.cnpj = i.fundo_cnpj
        WHERE i.fundo_cnpj IN ({placeholders})
        ORDER BY i.fundo_cnpj, i.data
    """, tuple(cnpjs))
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


def resgates_atipicos(minimo: float = 50_000) -> pd.DataFrame:
    return _q("""
        SELECT i.fundo_cnpj, e.razao_social AS fundo, i.data,
               i.resgate_dia, i.cotistas, i.pl
        FROM inf_diario i
        LEFT JOIN empresas e ON e.cnpj = i.fundo_cnpj
        WHERE i.resgate_dia >= ?
        ORDER BY i.resgate_dia DESC
    """, (minimo,))


def captacoes_atipicas(minimo: float = 50_000) -> pd.DataFrame:
    return _q("""
        SELECT i.fundo_cnpj, e.razao_social AS fundo, i.data,
               i.captacao_dia, i.cotistas, i.pl
        FROM inf_diario i
        LEFT JOIN empresas e ON e.cnpj = i.fundo_cnpj
        WHERE i.captacao_dia >= ?
        ORDER BY i.captacao_dia DESC
    """, (minimo,))


def evolucao_mensal(cnpj: str | None = None) -> pd.DataFrame:
    cond = "WHERE fundo_cnpj = ?" if cnpj else ""
    params = (cnpj,) if cnpj else ()
    return _q(f"""
        SELECT fundo_cnpj,
               SUBSTR(data, 1, 7) AS mes,
               ROUND(AVG(pl), 2)   AS pl_medio,
               ROUND(MIN(pl), 2)   AS pl_min,
               ROUND(MAX(pl), 2)   AS pl_max,
               ROUND(SUM(captacao_dia), 2) AS captacao_total,
               ROUND(SUM(resgate_dia), 2)  AS resgate_total,
               MIN(cotistas) AS cot_min,
               MAX(cotistas) AS cot_max
        FROM inf_diario
        {cond}
        GROUP BY fundo_cnpj, SUBSTR(data, 1, 7)
        ORDER BY fundo_cnpj, mes
    """, params)


def primeiro_e_ultimo_dia() -> pd.DataFrame:
    return _q("""
        SELECT i.fundo_cnpj, e.razao_social AS fundo,
               MIN(i.data) AS primeiro_dia,
               MAX(i.data) AS ultimo_dia,
               COUNT(*) AS dias_reportados,
               ROUND(AVG(i.pl), 2) AS pl_medio,
               ROUND(AVG(i.cotistas), 0) AS cot_medio
        FROM inf_diario i
        LEFT JOIN empresas e ON e.cnpj = i.fundo_cnpj
        GROUP BY i.fundo_cnpj
        ORDER BY ultimo_dia DESC
    """)


def fundos_com_nome(termo: str) -> pd.DataFrame:
    return _q("""
        SELECT DISTINCT e.cnpj, e.razao_social, e.situacao
        FROM empresas e
        JOIN papeis_fundo p ON p.fundo_cnpj = e.cnpj
        WHERE UPPER(e.razao_social) LIKE ?
        ORDER BY e.razao_social
    """, (_like(termo),))


def salvar(df: pd.DataFrame, nome: str) -> Path:
    saida = Path("data/exports") / f"{nome}.csv"
    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(saida, index=False, encoding="utf-8-sig")
    print(f"[CONSULTAS] salvo: {saida}")
    return saida


if __name__ == "__main__":
    print("\n=== RESUMO DO DATASET ===")
    print(resumo().to_string(index=False))

    print("\n=== TOP 10 PESSOAS POR Nº DE EMPRESAS ===")
    print(ranking_pessoas(10).to_string(index=False))

    print("\n=== PARTICIPACOES DE VORCARO ===")
    print(participacoes_de("VORCARO").to_string(index=False))

    print("\n=== TOP 5 GESTORAS PARCEIRAS ===")
    print(gestoras_top(5).to_string(index=False))

    print("\n=== PRIMEIRO E ULTIMO DIA DOS FUNDOS NO INF_DIARIO ===")
    print(primeiro_e_ultimo_dia().to_string(index=False))

    print("\n=== RESGATES ATIPICOS (>=50k) ===")
    print(resgates_atipicos().to_string(index=False))
