"""Follow-the-money de TODOS os entes públicos (RPPS) ligados ao Master, via DAIR (Carteira 2023-2026).
Saídas: timeline longo (todos x competência) + resumo por ente. polars."""
import sys, glob
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUTDIR = "investigacao-claude/dados"
ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))
MASTER_CNPJS = {"33923798000100","33884941000194","09526594000143","33886862000112",
                "46909301000133","53273475000118","32088041000178","29786909000107",
                "34081900000122","53311600000137","42584801000191","31368739000184",
                "28849674000184","58807049000130"}
NAME_RE = r"(?i)BANCO MASTER|MASTER S/?A|MASTER M[UÚ]LTIPLO|\bREAG\b|\bCBSF\b|HANS 95|SDG ?II|LANCIA|GOLD STYLE|\bKATCH\b|UPPER FUNDO|MARANTA|TERM[OÓ]PILAS|ABBIAMO|ANNA FUNDO"
NOME = "Nome do Fundo / Banco da Conta"
KEY = ["tier", "Ente", "UF", "CNPJ"]


def num(c): return (pl.col(c).cast(pl.String).str.replace_all(r"\.","").str.replace(",",".").cast(pl.Float64, strict=False))
def ck(): c = pl.col("Competência").cast(pl.String).str.zfill(6); return (c.str.slice(2,4)+c.str.slice(0,2))


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS], how="vertical_relaxed")
    idd = pl.col("Identificação do Ativo").cast(pl.String).str.replace_all(r"\D","")
    nome = pl.col(NOME).cast(pl.String)
    m = lf.filter(nome.str.contains(NAME_RE) | idd.is_in(list(MASTER_CNPJS))).collect()
    m = m.with_columns(num("Valor Total Atual").alias("valor"), num("Percentual de Recursos do RPPS").alias("pct"),
                       ck().alias("ck"),
                       pl.when(nome.str.contains(r"(?i)BANCO MASTER")).then(pl.lit("Tier1_LF_Master"))
                         .otherwise(pl.lit("Tier2_fundo_Reag")).alias("tier"))

    # TIMELINE LONGO (todos os entes x competência)
    ec = (m.group_by(KEY + ["ck", "Competência"]).agg(pl.col("valor").sum().alias("valor"),
                                                       pl.col("pct").max().alias("pct_carteira"))
            .sort(["tier", "Ente", "ck"]))
    ec.write_csv(f"{OUTDIR}/dair_follow_the_money_todos_rpps.csv")

    # RESUMO por ente (entrada, pico, valor na liquidação 202511, último, congelou?)
    base = ec.group_by(KEY).agg(
        pl.col("ck").n_unique().alias("n_comp"),
        pl.col("valor").max().alias("pico_valor"),
        pl.col("pct_carteira").max().alias("pct_pico"))
    entrada = ec.filter(pl.col("valor") > 0).group_by(KEY).agg(pl.col("ck").min().alias("entrada"))
    pico_ck = ec.sort("valor", descending=True).group_by(KEY, maintain_order=True).first().select(KEY + [pl.col("ck").alias("pico_ck")])
    liq = ec.filter(pl.col("ck") == "202511").group_by(KEY).agg(pl.col("valor").first().alias("valor_liquidacao"))
    ult = ec.sort("ck").group_by(KEY, maintain_order=True).last().select(KEY + [pl.col("valor").alias("valor_ultimo"), pl.col("ck").alias("ultima_comp")])
    res = (base.join(entrada, on=KEY, how="left").join(pico_ck, on=KEY, how="left")
               .join(liq, on=KEY, how="left").join(ult, on=KEY, how="left"))
    res = res.with_columns(
        ((pl.col("valor_ultimo") > 0) &
         ((pl.col("valor_ultimo") - pl.col("valor_liquidacao")).abs() <= 0.02 * pl.col("valor_liquidacao")))
        .alias("congelou_na_liquidacao")
    ).sort(["tier", "pico_valor"], descending=[False, True])
    res.write_csv(f"{OUTDIR}/dair_follow_the_money_resumo.csv")

    t1 = res.filter(pl.col("tier") == "Tier1_LF_Master")
    print(f"=== FOLLOW-THE-MONEY — TODOS os RPPS com LF do Banco Master (Tier-1): {t1.height} entes ===")
    with pl.Config(tbl_rows=40, fmt_str_lengths=32, tbl_width_chars=240):
        print(t1.select(["Ente","UF","entrada","pico_ck","pico_valor","pct_pico","valor_liquidacao","valor_ultimo","congelou_na_liquidacao"]))
    print(f"\nTier-1: {t1.height} entes | pico somado R$ {t1['pico_valor'].sum()/1e6:,.1f} mi | "
          f"congelaram na liquidação: {t1['congelou_na_liquidacao'].sum()}")
    t2 = res.filter(pl.col("tier") == "Tier2_fundo_Reag")
    print(f"Tier-2 (fundos Reag): {t2.height} entes | pico somado R$ {t2['pico_valor'].sum()/1e6:,.1f} mi")
    print(f"\nCSVs: dair_follow_the_money_todos_rpps.csv (longo) + dair_follow_the_money_resumo.csv")


if __name__ == "__main__":
    main()
