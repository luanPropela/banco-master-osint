"""DEFINITIVO — entes públicos com produtos do Banco Master no DAIR, filtro completo+preciso.
Tier-1 = Letra Financeira/CDB emitido pelo BANCO MASTER (qualquer variante de nome, tipo renda fixa IF).
Tier-2 = fundos da rede Reag/fraude (por nome ou CNPJ). Exclui 'Master' genérico (Safra/BB/Banrisul...)."""
import sys, glob
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = "investigacao-claude/dados"
ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))
NOME = "Nome do Fundo / Banco da Conta"; IDA = "Identificação do Ativo"
FRAUDE_CNPJ = {"46909301000133","53273475000118","32088041000178","29786909000107","34081900000122",
               "53311600000137","42584801000191","31368739000184","28849674000184","58807049000130"}
KEY = ["tier", "Ente", "UF"]


def num(c): return (pl.col(c).cast(pl.String).str.replace_all(r"\.","").str.replace(",",".").cast(pl.Float64, strict=False))
def ckexpr(): c = pl.col("Competência").cast(pl.String).str.zfill(6); return (c.str.slice(2,4)+c.str.slice(0,2))


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS], how="vertical_relaxed").collect()
    nome = pl.col(NOME).cast(pl.String); tipo = pl.col("Tipo de Ativo").cast(pl.String)
    iddig = pl.col(IDA).cast(pl.String).str.replace_all(r"\D","")

    # Tier-1: LF/CDB do Banco Master (emissor = Master). Renda fixa de IF com 'master' no nome, OU 'banco master'.
    is_rf_if = tipo.str.contains(r"(?i)renda fixa") & tipo.str.contains(r"(?i)institui|obriga")
    is_master_lf = (nome.str.contains(r"(?i)banco master")
                    | (nome.str.contains(r"(?i)master") & is_rf_if)
                    | nome.str.contains(r"(?i)^\s*141 - BANCO MASTER"))
    # Tier-2: rede Reag/fraude (fundos)
    is_reag = (nome.str.contains(r"(?i)\breag\b|\bcbsf\b|hans 95|sdg ?ii|lancia|gold style|\bkatch\b|anna fundo|term[oó]pilas|abbiamo")
               | iddig.is_in(list(FRAUDE_CNPJ)))
    m = lf.filter(is_master_lf | is_reag).with_columns(
        num("Valor Total Atual").alias("valor"), num("Percentual de Recursos do RPPS").alias("pct"),
        ckexpr().alias("ck"),
        pl.when(is_master_lf).then(pl.lit("Tier1_LF_CDB_Master")).otherwise(pl.lit("Tier2_fundo_Reag")).alias("tier"))

    # posição por ente/competência (soma de papéis), depois pico
    ec = m.group_by(KEY + ["CNPJ", "ck", "Competência"]).agg(pl.col("valor").sum().alias("v"), pl.col("pct").max().alias("p"))
    pico = ec.sort("v", descending=True).group_by(KEY + ["CNPJ"], maintain_order=True).first().select(KEY+["CNPJ", pl.col("v").alias("pico"), pl.col("p").alias("pct_pico"), pl.col("ck").alias("pico_ck")])
    ent = ec.filter(pl.col("v") > 0).group_by(KEY+["CNPJ"]).agg(pl.col("ck").min().alias("entrada"))
    liq = ec.filter(pl.col("ck") == "202511").group_by(KEY+["CNPJ"]).agg(pl.col("v").first().alias("v_liq"))
    ult = ec.sort("ck").group_by(KEY+["CNPJ"], maintain_order=True).last().select(KEY+["CNPJ", pl.col("v").alias("v_ult")])
    inv = (pico.join(ent, on=KEY+["CNPJ"], how="left").join(liq, on=KEY+["CNPJ"], how="left").join(ult, on=KEY+["CNPJ"], how="left")
               .with_columns(pl.when((pl.col("v_ult")>0)&((pl.col("v_ult")-pl.col("v_liq")).abs()<=0.02*pl.col("v_liq"))).then(pl.lit("congelado"))
                             .when((pl.col("v_liq")>1e5)&(pl.col("v_ult")<1e4)).then(pl.lit("baixado_a_zero"))
                             .otherwise(pl.lit("outro")).alias("destino"))
               .sort(["tier","pico"], descending=[False, True]))
    inv.write_csv(f"{OUT}/dair_rpps_master_DEFINITIVO.csv")
    ec.sort(KEY+["ck"]).write_csv(f"{OUT}/dair_follow_the_money_DEFINITIVO.csv")

    t1 = inv.filter(pl.col("tier") == "Tier1_LF_CDB_Master")
    print(f"=== TIER-1 (LF/CDB do BANCO MASTER) — {t1.height} entes públicos | pico somado R$ {t1['pico'].sum()/1e6:,.1f} mi ===")
    with pl.Config(tbl_rows=60, fmt_str_lengths=34, tbl_width_chars=200):
        print(t1.select(["Ente","UF","entrada","pico_ck","pico","pct_pico","destino"]))
    t2 = inv.filter(pl.col("tier") == "Tier2_fundo_Reag")
    print(f"\n=== TIER-2 (fundos rede Reag) — {t2.height} entes | pico somado R$ {t2['pico'].sum()/1e6:,.1f} mi ===")
    with pl.Config(tbl_rows=40, fmt_str_lengths=30, tbl_width_chars=160):
        print(t2.select(["Ente","UF","pico","pct_pico","destino"]).head(40))
    print(f"\nTotal entes públicos (Tier1∪Tier2): {inv.select(['Ente','UF']).unique().height}")
    print(f"CSVs: dair_rpps_master_DEFINITIVO.csv + dair_follow_the_money_DEFINITIVO.csv")


if __name__ == "__main__":
    main()
