import json
import sqlite3
from pathlib import Path

DB_PATH = Path("data/master.db")
CACHE_RECEITA = Path("data/cnpjs.json")
CACHE_B2B = Path("data/fundos_b2b.json")

PAPEIS_CVM = [
    ("CNPJ_ADMIN",         "ADMIN",            "admin"),
    ("CNPJ_ADMINISTRADOR", "NM_ADMINISTRADOR", "admin"),
    ("CPF_CNPJ_GESTOR",    "GESTOR",           "gestor"),
    ("CNPJ_CUSTODIANTE",   "CUSTODIANTE",      "custodiante"),
    ("CNPJ_CONTROLADOR",   "CONTROLADOR",      "controlador"),
]

def _so_digitos(texto) -> str:
    if texto is None:
        return ""
    return "".join(filter(str.isdigit, str(texto)))

SCHEMA = """
DROP TABLE IF EXISTS empresas;
DROP TABLE IF EXISTS pessoas;
DROP TABLE IF EXISTS participacoes;
DROP TABLE IF EXISTS papeis_fundo;

CREATE TABLE empresas (
    cnpj            TEXT PRIMARY KEY,
    razao_social    TEXT,
    uf              TEXT,
    situacao        TEXT,
    capital_social  REAL,
    cnae            TEXT,
    fonte           TEXT
);

CREATE TABLE pessoas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT UNIQUE,
    faixa_etaria    TEXT
);

CREATE TABLE participacoes (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa_cnpj       TEXT NOT NULL,
    socio_pessoa_id    INTEGER NOT NULL DEFAULT 0,   -- 0 = participação PJ→PJ
    socio_empresa_cnpj TEXT    NOT NULL DEFAULT '',  -- '' = participação PF→PJ
    qualificacao       TEXT    NOT NULL DEFAULT '',
    data_entrada       TEXT,
    fonte              TEXT,
    UNIQUE (empresa_cnpj, socio_pessoa_id, socio_empresa_cnpj, qualificacao),
    FOREIGN KEY (empresa_cnpj) REFERENCES empresas(cnpj)
);

CREATE TABLE papeis_fundo (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    fundo_cnpj      TEXT NOT NULL,
    papel           TEXT NOT NULL,
    prestador_cnpj  TEXT,
    prestador_nome  TEXT,
    FOREIGN KEY (fundo_cnpj) REFERENCES empresas(cnpj)
);

CREATE INDEX idx_part_empresa ON participacoes(empresa_cnpj);
CREATE INDEX idx_part_pessoa  ON participacoes(socio_pessoa_id);
CREATE INDEX idx_part_socio_pj ON participacoes(socio_empresa_cnpj);
CREATE INDEX idx_papel_fundo  ON papeis_fundo(fundo_cnpj);
CREATE INDEX idx_papel_prest  ON papeis_fundo(prestador_cnpj);
"""

def criar_schema(con: sqlite3.Connection) -> None:
    con.executescript(SCHEMA)
    con.commit()
    print("[DB] schema criado")

def _upsert_pessoa(con: sqlite3.Connection, nome: str, faixa: str = "") -> int:
    cur = con.execute("SELECT id FROM pessoas WHERE nome = ?", (nome,))
    linha = cur.fetchone()
    if linha:
        return linha[0]
    cur = con.execute(
        "INSERT INTO pessoas (nome, faixa_etaria) VALUES (?, ?)",
        (nome, faixa or "")
    )
    return cur.lastrowid

def _upsert_empresa(con: sqlite3.Connection, cnpj: str, **dados) -> None:
    cur = con.execute("SELECT cnpj FROM empresas WHERE cnpj = ?", (cnpj,))
    if cur.fetchone() is None:
        con.execute("""
            INSERT INTO empresas (cnpj, razao_social, uf, situacao,
                                  capital_social, cnae, fonte)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cnpj,
              dados.get("razao_social", ""),
              dados.get("uf", ""),
              dados.get("situacao", ""),
              dados.get("capital_social") or None,
              dados.get("cnae", ""),
              dados.get("fonte", "")))
        return

    for campo in ("razao_social", "uf", "situacao", "cnae"):
        valor = dados.get(campo)
        if valor:
            con.execute(
                f"UPDATE empresas SET {campo} = ? "
                f"WHERE cnpj = ? AND (COALESCE({campo}, '') = '')",
                (valor, cnpj)
            )

def _capital_float(valor) -> float | None:
    if valor in (None, ""):
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None

def carregar_receita(con: sqlite3.Connection, dados: dict) -> None:
    print(f"[DB] carregando {len(dados)} empresa(s) da Receita")
    for cnpj, info in dados.items():
        cnpj = _so_digitos(cnpj)
        _upsert_empresa(
            con, cnpj,
            razao_social=info.get("razao_social", ""),
            uf=info.get("uf", ""),
            situacao=info.get("descricao_situacao_cadastral", ""),
            capital_social=_capital_float(info.get("capital_social")),
            cnae=info.get("cnae_fiscal_descricao", ""),
            fonte="minha_receita",
        )

        for socio in info.get("qsa", []) or []:
            nome = (socio.get("nome_socio") or "").strip()
            if not nome:
                continue

            identificador = socio.get("identificador_de_socio")
            cpf_cnpj = _so_digitos(socio.get("cnpj_cpf_do_socio", ""))

            qualif = socio.get("qualificacao_socio", "") or ""
            data_ent = socio.get("data_entrada_sociedade", "")

            if identificador == 1 and len(cpf_cnpj) == 14:

                _upsert_empresa(con, cpf_cnpj,
                                razao_social=nome, fonte="minha_receita_qsa")
                con.execute("""
                    INSERT OR IGNORE INTO participacoes
                        (empresa_cnpj, socio_pessoa_id, socio_empresa_cnpj,
                         qualificacao, data_entrada, fonte)
                    VALUES (?, 0, ?, ?, ?, ?)
                """, (cnpj, cpf_cnpj, qualif, data_ent, "minha_receita"))
            else:

                pid = _upsert_pessoa(con, nome, socio.get("faixa_etaria", ""))
                con.execute("""
                    INSERT OR IGNORE INTO participacoes
                        (empresa_cnpj, socio_pessoa_id, socio_empresa_cnpj,
                         qualificacao, data_entrada, fonte)
                    VALUES (?, ?, '', ?, ?, ?)
                """, (cnpj, pid, qualif, data_ent, "minha_receita"))

def carregar_b2b(con: sqlite3.Connection, dados: dict) -> None:
    fundos = dados.get("fundos_fi", []) + dados.get("fundos_fii", [])
    print(f"[DB] carregando {len(fundos)} fundo(s) da CVM")

    for linha in fundos:
        cnpj = _so_digitos(linha.get("CNPJ_FUNDO", ""))
        if not cnpj:
            continue
        nome = linha.get("DENOM_SOCIAL") or linha.get("NM_FUNDO") or cnpj
        _upsert_empresa(con, cnpj,
                        razao_social=nome,
                        situacao=linha.get("SIT", ""),
                        cnae="FUNDO DE INVESTIMENTO",
                        fonte="cvm")

        for col_cnpj, col_nome, papel in PAPEIS_CVM:
            prestador_cnpj = _so_digitos(linha.get(col_cnpj, ""))
            prestador_nome = (linha.get(col_nome) or "").strip()
            if not prestador_cnpj and not prestador_nome:
                continue
            con.execute("""
                INSERT INTO papeis_fundo
                    (fundo_cnpj, papel, prestador_cnpj, prestador_nome)
                VALUES (?, ?, ?, ?)
            """, (cnpj, papel, prestador_cnpj or None, prestador_nome or None))

            if len(prestador_cnpj) == 14:
                _upsert_empresa(con, prestador_cnpj,
                                razao_social=prestador_nome, fonte="cvm_papel")

    qsa_pacote = dados.get("qsa") or {}
    print(f"[DB] carregando QSA de {len(qsa_pacote)} entidade(s) Master (fase 2)")
    carregar_receita(con, qsa_pacote)

def resumo(con: sqlite3.Connection) -> None:
    print("\n[DB] === RESUMO ===")
    for tabela in ("empresas", "pessoas", "participacoes", "papeis_fundo"):
        (n,) = con.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()
        print(f"  {tabela:15} {n:>5}")

    print("\npessoas com mais participações:")
    rows = con.execute("""
        SELECT p.nome, COUNT(*) AS quantas
        FROM participacoes pa
        JOIN pessoas p ON p.id = pa.socio_pessoa_id
        GROUP BY p.nome
        ORDER BY quantas DESC
        LIMIT 10
    """).fetchall()
    for nome, quantas in rows:
        print(f"  {quantas:>2}  {nome}")

    print("\npapéis por tipo (fundos CVM):")
    rows = con.execute("""
        SELECT papel, COUNT(*) FROM papeis_fundo GROUP BY papel ORDER BY 2 DESC
    """).fetchall()
    for papel, n in rows:
        print(f"  {n:>4}  {papel}")

def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        criar_schema(con)

        if CACHE_RECEITA.exists():
            with CACHE_RECEITA.open(encoding="utf-8") as f:
                carregar_receita(con, json.load(f))
        else:
            print(f"[DB] aviso: {CACHE_RECEITA} não encontrado, pulando fase 1")

        if CACHE_B2B.exists():
            with CACHE_B2B.open(encoding="utf-8") as f:
                carregar_b2b(con, json.load(f))
        else:
            print(f"[DB] aviso: {CACHE_B2B} não encontrado, pulando fase 2")

        con.commit()
        resumo(con)
        print(f"\n[DB] salvo: {DB_PATH.resolve()}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
