"""Investiga como a RioPrevidência aparece no DAIR e o que ela tem de Master."""
import sys, glob
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS],
                   how="vertical_relaxed")
    cnpj = pl.col("CNPJ").cast(pl.String).str.replace_all(r"\D", "")
    # 1) RioPrev existe no DAIR? por CNPJ e por nome
    rio = lf.filter((cnpj == "03066219000181")
                    | pl.col("Ente").cast(pl.String).str.contains(r"(?i)rioprev|previd[eê]ncia.*rio de janeiro|fundo [uú]nico")).collect()
    print(f"linhas de RioPrev (por CNPJ 03066219000181 / nome): {rio.height}")
    if rio.height:
        print("Entes/CNPJs casados:")
        print(rio.group_by(["Ente", "CNPJ", "UF"]).agg(pl.len().alias("linhas")))
        print("\nCompetências presentes:", sorted(rio["Competência"].unique().to_list())[:50])
        # o que RioPrev tem de Master?
        master = rio.filter(pl.col("Nome do Fundo / Banco da Conta").cast(pl.String).str.contains(r"(?i)MASTER|REAG|CBSF|HANS|SDG|ANNA|LANCIA"))
        print(f"\nlinhas de RioPrev ligadas a Master/Reag: {master.height}")
        with pl.Config(tbl_rows=20, fmt_str_lengths=45, tbl_width_chars=200):
            print(master.select(["Competência", "Tipo de Ativo", "Nome do Fundo / Banco da Conta", "Valor Total Atual"]).head(20))

    # 2) todos os Entes cujo nome contém RIO (para achar variantes)
    print("\n=== Entes distintos contendo 'RIO' (amostra) ===")
    rios = lf.filter(pl.col("Ente").cast(pl.String).str.contains(r"(?i)\brio\b|rioprev")).select(["Ente", "CNPJ", "UF"]).unique().collect()
    with pl.Config(tbl_rows=40, fmt_str_lengths=50, tbl_width_chars=160):
        print(rios)


if __name__ == "__main__":
    main()
