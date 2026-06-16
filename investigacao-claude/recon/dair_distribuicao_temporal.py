"""Como o dinheiro público se distribuiu ao longo do tempo: pivô ente x competência + gráfico.
Lê dair_follow_the_money_todos_rpps.csv (já gerado). polars + matplotlib."""
import sys
import polars as pl
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = "investigacao-claude/dados"
LONG = f"{OUT}/dair_follow_the_money_todos_rpps.csv"
MARCOS = ["202312", "202406", "202412", "202506", "202510", "202512", "202602"]  # marcos anuais/chave


def main():
    df = pl.read_csv(LONG).filter(pl.col("tier") == "Tier1_LF_Master")
    df = df.with_columns(pl.col("ck").cast(pl.String), (pl.col("valor") / 1e6).alias("mi"))

    # PIVÔ ente x competência (R$ mi) — só marcos
    piv = (df.filter(pl.col("ck").is_in(MARCOS))
             .pivot(values="mi", index=["Ente", "UF"], on="ck", aggregate_function="sum")
             .sort(MARCOS[-2] if MARCOS[-2] in df.columns else "Ente", descending=True, nulls_last=True))
    cols_presentes = [c for c in MARCOS if c in piv.columns]
    piv = piv.select(["Ente", "UF"] + cols_presentes).sort(cols_presentes[-1], descending=True, nulls_last=True)
    print("=== Posição em LF do Banco Master (R$ milhões), por ente x competência ===")
    with pl.Config(tbl_rows=40, fmt_str_lengths=30, tbl_width_chars=200):
        print(piv)

    # TOTAL público no Master por competência (curva de acúmulo)
    tot = df.group_by("ck").agg(pl.col("mi").sum().alias("total_mi"),
                                pl.col("Ente").n_unique().alias("n_rpps")).sort("ck")
    print("\n=== Total de dinheiro público (RPPS) em LF do Master, por competência ===")
    with pl.Config(tbl_rows=60, tbl_width_chars=80):
        print(tot)

    # GRÁFICO: linhas dos top entes + total
    top = (df.group_by("Ente").agg(pl.col("mi").max().alias("pk")).sort("pk", descending=True).head(6)["Ente"].to_list())
    plt.figure(figsize=(13, 7))
    xs_all = sorted(df["ck"].unique().to_list())
    xi = {c: i for i, c in enumerate(xs_all)}
    for ente in top:
        sub = df.filter(pl.col("Ente") == ente).sort("ck")
        plt.plot([xi[c] for c in sub["ck"]], sub["mi"], marker="o", ms=3, label=ente)
    sub = tot.sort("ck")
    plt.plot([xi[c] for c in sub["ck"]], sub["total_mi"], color="#0C253A", lw=3, ls="--", label="TOTAL (todos RPPS)")
    plt.axvline(xi.get("202511", 0), color="#C0392B", ls=":", lw=2)
    plt.text(xi.get("202511", 0), plt.ylim()[1]*0.95, " liquidação 11/2025", color="#C0392B", fontsize=9)
    step = max(1, len(xs_all)//12)
    plt.xticks([xi[c] for c in xs_all[::step]], [f"{c[4:]}/{c[:4]}" for c in xs_all[::step]], rotation=45, fontsize=8)
    plt.ylabel("R$ milhões em LF do Banco Master"); plt.legend(fontsize=8); plt.grid(alpha=0.3)
    plt.title("Dinheiro público (RPPS) no Banco Master ao longo do tempo")
    plt.tight_layout(); plt.savefig(f"{OUT}/dair_distribuicao_temporal.png", dpi=140)
    piv.write_csv(f"{OUT}/dair_distribuicao_temporal_pivot.csv")
    print(f"\n-> {OUT}/dair_distribuicao_temporal.png + _pivot.csv")


if __name__ == "__main__":
    main()
