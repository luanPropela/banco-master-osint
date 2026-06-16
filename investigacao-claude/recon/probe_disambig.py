"""Desambigua Banco Master/Reag REAL vs 'Master' genérico no DAIR, usando CNPJ em Identificação do Ativo."""
import sys, glob
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))
NOME = "Nome do Fundo / Banco da Conta"; IDA = "Identificação do Ativo"
FRAUDE_CNPJ = {"46909301000133","53273475000118","32088041000178","29786909000107","34081900000122",
               "53311600000137","42584801000191","31368739000184","28849674000184","58807049000130",
               "33923798000100","33884941000194","09526594000143","33886862000112"}


def num(c): return (pl.col(c).cast(pl.String).str.replace_all(r"\.","").str.replace(",",".").cast(pl.Float64, strict=False))


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS], how="vertical_relaxed")
    nome = pl.col(NOME).cast(pl.String); iddig = pl.col(IDA).cast(pl.String).str.replace_all(r"\D","")
    u = lf.filter(nome.str.contains(r"(?i)master|reag|cbsf|hans 95|sdg ?ii|lancia|gold style|katch|anna fundo")).collect()
    u = u.with_columns(num("Valor Total Atual").alias("v"), iddig.alias("iddig"))

    # mapa nome -> CNPJ (iddig de 14) + nº entes + valor — para classificar
    mp = (u.with_columns((pl.col("iddig").str.len_chars() == 14).alias("tem_cnpj"))
            .group_by([NOME]).agg(pl.col("iddig").filter(pl.col("iddig").str.len_chars()==14).first().alias("cnpj"),
                                  pl.col("Ente").n_unique().alias("entes"), pl.col("v").sum().alias("v_soma"))
            .sort("v_soma", descending=True))
    mp = mp.with_columns(pl.col("cnpj").is_in(list(FRAUDE_CNPJ)).alias("cnpj_fraude"))
    print("=== nomes 'master/reag' matchados: nome | CNPJ | entes | é CNPJ da fraude? ===")
    with pl.Config(tbl_rows=45, fmt_str_lengths=52, tbl_width_chars=180):
        print(mp.head(45))

    # quais CNPJs distintos (14d) aparecem e quantos batem com a fraude
    cnpjs = u.filter(pl.col("iddig").str.len_chars()==14)["iddig"].unique().to_list()
    print(f"\nCNPJs (14d) distintos nos matches: {len(cnpjs)} | batem com rede fraude: {sorted(set(cnpjs)&FRAUDE_CNPJ)}")

    # São Roque e Gov RJ — o que exatamente têm?
    for termo in ["roque", "Governo do Estado do Rio de Janeiro", "Amazonas", "Senador Canedo"]:
        sub = u.filter(pl.col("Ente").cast(pl.String).str.contains(f"(?i){termo}"))
        if sub.height:
            print(f"\n=== {termo}: {sub.height} linhas master/reag ===")
            with pl.Config(tbl_rows=6, fmt_str_lengths=48, tbl_width_chars=170):
                print(sub.select(["Ente","Competência",NOME,"iddig","Tipo de Ativo","Valor Total Atual"]).unique().head(6))


if __name__ == "__main__":
    main()
