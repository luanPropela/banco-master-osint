"""
Entes públicos (RPPS) que financiaram o Banco Master, via DAIR (Carteira 2023-2026) — polars.
- Inventário (Tier-1: Letra Financeira do próprio Banco Master; Tier-2: fundos Reag).
- Follow-the-money temporal de UM ente (default Maceió): trajetória mensal da posição em Master.
Saídas em investigacao-claude/dados/.
"""
import sys, glob
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUTDIR = "investigacao-claude/dados"
ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))
ALVO_FOLLOW = "Maceió"   # ente para o follow-the-money temporal

MASTER_CNPJS = {"33923798000100","33884941000194","09526594000143","33886862000112",
                "46909301000133","53273475000118","32088041000178","29786909000107",
                "34081900000122","53311600000137","42584801000191","31368739000184",
                "28849674000184","58807049000130"}
NAME_RE = r"(?i)BANCO MASTER|MASTER S/?A|MASTER M[UÚ]LTIPLO|\bREAG\b|\bCBSF\b|HANS 95|SDG ?II|LANCIA|GOLD STYLE|\bKATCH\b|UPPER FUNDO|MARANTA|TERM[OÓ]PILAS|ABBIAMO|ANNA FUNDO"
NOME = "Nome do Fundo / Banco da Conta"


def num(col):
    return (pl.col(col).cast(pl.String).str.replace_all(r"\.", "").str.replace(",", ".").cast(pl.Float64, strict=False))


def comp_key():  # "MMAAAA" -> "AAAAMM" para ordenar
    c = pl.col("Competência").cast(pl.String).str.zfill(6)
    return (c.str.slice(2, 4) + c.str.slice(0, 2))


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS],
                   how="vertical_relaxed")
    idd = pl.col("Identificação do Ativo").cast(pl.String).str.replace_all(r"\D", "")
    nome = pl.col(NOME).cast(pl.String)
    m = lf.filter(nome.str.contains(NAME_RE) | idd.is_in(list(MASTER_CNPJS))).collect()
    m = m.with_columns(
        num("Valor Total Atual").alias("valor"),
        num("Percentual de Recursos do RPPS").alias("pct_rpps"),
        comp_key().alias("ck"),
        pl.when(nome.str.contains(r"(?i)BANCO MASTER")).then(pl.lit("Tier1: LF Banco Master"))
          .otherwise(pl.lit("Tier2: fundo Reag/grupo")).alias("tier"),
    )
    print(f"linhas Master/Reag: {m.height} | Tier1 LF Master: {m.filter(pl.col('tier').str.starts_with('Tier1')).height}")

    # INVENTÁRIO por ente + tier (posição = SOMA dos papéis por competência; pico = máx ao longo do tempo)
    por_comp = (m.group_by(["tier", "Ente", "UF", "CNPJ", "ck"])
                  .agg(pl.col("valor").sum().alias("valor_comp"), pl.col("pct_rpps").max().alias("pct_comp")))
    inv = (por_comp.group_by(["tier", "Ente", "UF", "CNPJ"])
             .agg(pl.col("valor_comp").max().alias("valor_pico"),
                  pl.col("pct_comp").max().alias("pct_pico_carteira"),
                  pl.col("ck").min().alias("primeira_comp"), pl.col("ck").max().alias("ultima_comp"),
                  pl.col("ck").n_unique().alias("n_competencias"))
             .sort(["tier", "valor_pico"], descending=[False, True]))
    inv.write_csv(f"{OUTDIR}/dair_rpps_expostos_master.csv")

    t1 = inv.filter(pl.col("tier").str.starts_with("Tier1"))
    print(f"\n=== INVENTÁRIO Tier-1 (dinheiro público DIRETO em LF do Banco Master): {t1.height} RPPS ===")
    with pl.Config(tbl_rows=40, fmt_str_lengths=34, tbl_width_chars=200):
        print(t1.select(["Ente", "UF", "valor_pico", "pct_pico_carteira", "primeira_comp", "ultima_comp", "n_competencias"]))
    print(f"\nTier-1 total de RPPS: {t1.height} | soma dos picos: R$ {t1['valor_pico'].sum()/1e6:,.1f} mi")
    t2 = inv.filter(pl.col('tier').str.starts_with('Tier2'))
    print(f"Tier-2 (fundos Reag/grupo): {t2.height} RPPS")

    # FOLLOW-THE-MONEY temporal de UM ente
    ente = m.filter(pl.col("Ente").cast(pl.String).str.contains(f"(?i){ALVO_FOLLOW}")
                    & pl.col("tier").str.starts_with("Tier1"))
    traj = (ente.group_by(["ck", "Competência"]).agg(
                pl.col("valor").sum().alias("valor_master"),
                pl.col("pct_rpps").max().alias("pct_carteira"),
                pl.col(NOME).n_unique().alias("n_papeis"))
            .sort("ck"))
    traj.write_csv(f"{OUTDIR}/dair_follow_{ALVO_FOLLOW.lower()}_master_timeline.csv")
    print(f"\n=== FOLLOW-THE-MONEY: {ALVO_FOLLOW} — posição em LF do Banco Master, mês a mês ===")
    with pl.Config(tbl_rows=60, tbl_width_chars=120):
        print(traj.select(["Competência", "valor_master", "pct_carteira", "n_papeis"]))
    print(f"\nCSVs salvos em {OUTDIR}/  (inventário + timeline {ALVO_FOLLOW})")


if __name__ == "__main__":
    main()
