"""COMPLETUDE: temos todos os entes públicos com produtos do Master?
Match amplo (nome MASTER) + por CNPJ do emissor + quebra por tipo de produto +
checagem nominal dos entes citados na imprensa. polars."""
import sys, glob
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))
NOME = "Nome do Fundo / Banco da Conta"
IDA = "Identificação do Ativo"
MASTER_EMISSOR = ["33923798", "33884941", "09526594", "33886862"]  # raízes CNPJ bancos Master
NOTICIA = ["roque", "amap", "amprev", "macei", "cajamar", "itagua", "previd"]  # entes/termos citados


def num(c): return (pl.col(c).cast(pl.String).str.replace_all(r"\.","").str.replace(",",".").cast(pl.Float64, strict=False))


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS], how="vertical_relaxed")
    nome = pl.col(NOME).cast(pl.String); idd = pl.col(IDA).cast(pl.String)
    iddig = idd.str.replace_all(r"\D", "")
    cnpj_re = "|".join(MASTER_EMISSOR)

    # (A) o que está em 'Identificação do Ativo' nas linhas BANCO MASTER (descobrir se traz CNPJ do emissor)
    bm = lf.filter(nome.str.contains(r"(?i)BANCO MASTER")).collect()
    print("=== (A) amostra de 'Identificação do Ativo' p/ linhas BANCO MASTER ===")
    print(bm.select([IDA, NOME, "Tipo de Ativo"]).unique().head(8))

    # (B) UNIVERSO AMPLO: nome ~MASTER OU identificação contém CNPJ emissor Master
    universo = lf.filter(nome.str.contains(r"(?i)master") | iddig.str.contains(cnpj_re)).collect()
    universo = universo.with_columns(num("Valor Total Atual").alias("v"))
    print(f"\n=== (B) UNIVERSO AMPLO: {universo.height} linhas | entes distintos: {universo['Ente'].n_unique()} ===")
    print("por Tipo de Ativo:")
    with pl.Config(tbl_rows=20, fmt_str_lengths=55, tbl_width_chars=160):
        print(universo.group_by("Tipo de Ativo").agg(pl.len().alias("linhas"), pl.col("Ente").n_unique().alias("entes")).sort("linhas", descending=True))

    # entes com pico de posição (amplo) — lista completa
    por = (universo.group_by(["Ente", "UF"]).agg(pl.col("v").max().alias("pico"),
            pl.col(NOME).str.contains(r"(?i)BANCO MASTER").any().alias("tem_LF_master_direto")).sort("pico", descending=True))
    print(f"\n=== (B2) TODOS os entes do universo amplo: {por.height} ===")
    with pl.Config(tbl_rows=50, fmt_str_lengths=34, tbl_width_chars=160):
        print(por)

    # (C) entes citados na imprensa — estão? como aparecem?
    print("\n=== (C) checagem nominal dos entes citados na imprensa ===")
    for termo in NOTICIA:
        ents = lf.filter(pl.col("Ente").cast(pl.String).str.contains(f"(?i){termo}")).select(["Ente", "UF"]).unique().collect()
        nomes = ents["Ente"].to_list()
        # quais desses têm Master?
        comm = universo.filter(pl.col("Ente").is_in(nomes))["Ente"].unique().to_list() if nomes else []
        print(f"  '{termo}': entes={nomes[:6]}{'...' if len(nomes)>6 else ''} | COM MASTER: {comm}")


if __name__ == "__main__":
    main()
