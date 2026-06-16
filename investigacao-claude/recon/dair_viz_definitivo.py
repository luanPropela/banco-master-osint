"""Regenera distribuição temporal + grafo de financiamento com o conjunto DEFINITIVO (filtro corrigido)."""
import sys
import polars as pl
import networkx as nx
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = "investigacao-claude/dados"
T1 = "Tier1_LF_CDB_Master"


def main():
    long = pl.read_csv(f"{OUT}/dair_follow_the_money_DEFINITIVO.csv").filter(pl.col("tier") == T1)
    long = long.with_columns((pl.col("v")/1e6).alias("mi"), pl.col("ck").cast(pl.String))
    inv = pl.read_csv(f"{OUT}/dair_rpps_master_DEFINITIVO.csv").filter((pl.col("tier") == T1) & (pl.col("pico") > 0))

    # --- distribuição temporal ---
    tot = long.group_by("ck").agg(pl.col("mi").sum().alias("total"), pl.col("Ente").n_unique().alias("n")).sort("ck")
    print("=== total dinheiro público (Tier-1) em LF do Master por competência ===")
    with pl.Config(tbl_rows=40, tbl_width_chars=70): print(tot)
    xs = sorted(long["ck"].unique().to_list()); xi = {c: i for i, c in enumerate(xs)}
    plt.figure(figsize=(13, 7))
    top = inv.sort("pico", descending=True).head(6)["Ente"].to_list()
    for e in top:
        s = long.filter(pl.col("Ente") == e).sort("ck")
        plt.plot([xi[c] for c in s["ck"]], s["mi"], marker="o", ms=3, label=e[:28])
    s = tot.sort("ck"); plt.plot([xi[c] for c in s["ck"]], s["total"], "--", lw=3, color="#0C253A", label="TOTAL (18 RPPS)")
    plt.axvline(xi.get("202511", 0), color="#C0392B", ls=":", lw=2); plt.text(xi.get("202511",0), plt.ylim()[1]*0.9, " liquidação 11/2025", color="#C0392B", fontsize=9)
    step = max(1, len(xs)//12); plt.xticks([xi[c] for c in xs[::step]], [f"{c[4:]}/{c[:4]}" for c in xs[::step]], rotation=45, fontsize=8)
    plt.ylabel("R$ milhões em LF/CDB do Banco Master"); plt.legend(fontsize=8); plt.grid(alpha=0.3)
    plt.title("Dinheiro público (RPPS) no Banco Master ao longo do tempo — conjunto corrigido")
    plt.tight_layout(); plt.savefig(f"{OUT}/dair_distribuicao_temporal.png", dpi=140); plt.close()

    # --- grafo ---
    G = nx.DiGraph(); M = "BANCO MASTER"; G.add_node(M, layer=1, tipo="banco", valor=0)
    for r in inv.iter_rows(named=True):
        n = f"{r['Ente']}/{r['UF']}"
        G.add_node(n, layer=0, tipo="rpps", valor=r["pico"], pct=r["pct_pico"] or 0, destino=r["destino"])
        G.add_edge(n, M, rel="aportou_em", valor=r["pico"])
    G.add_node("SDG II FIDC", layer=2, tipo="fidc", valor=3.36e9); G.add_edge(M, "SDG II FIDC", rel="cessao", valor=1.129e9)
    for d, v in [("Lormont (Tanure)", 5.97e8), ("Banvox", 3.8e8), ("Super Empreend.", 2.2e7)]:
        G.add_node(d, layer=3, tipo="devedor", valor=v); G.add_edge("SDG II FIDC", d, rel="credito", valor=v)
    nx.write_graphml(G, f"{OUT}/grafo_financiamento_publico.graphml")
    pos = nx.multipartite_layout(G, subset_key="layer", scale=2.6)
    cor = {"rpps": "#BAD9F5", "banco": "#0C253A", "fidc": "#C0392B", "devedor": "#C0B394"}
    plt.figure(figsize=(18, 12))
    nx.draw_networkx_edges(G, pos, width=[max(.6,(d['valor']/1e6)*0.02) for *_,d in G.edges(data=True)],
                           edge_color=["#56666F" if d["rel"]=="aportou_em" else "#C0392B" for *_,d in G.edges(data=True)], alpha=.5, arrowsize=10)
    nx.draw_networkx_nodes(G, pos, node_size=[max(400,(G.nodes[n].get("valor",0)/1e6)*6+400) for n in G.nodes],
                           node_color=[cor[G.nodes[n]["tipo"]] for n in G.nodes], edgecolors="#0C253A", linewidths=.5)
    lbl = {n: (n if G.nodes[n]["tipo"]!="rpps" else f"{n}\nR$ {G.nodes[n]['valor']/1e6:.0f}mi·{G.nodes[n]['pct']:.0f}%") for n in G.nodes}
    nx.draw_networkx_labels(G, pos, lbl, font_size=6.5)
    plt.title("Financiamento público do Banco Master (18 RPPS, R$1,53 bi) → ocultação no SDG II", fontsize=12)
    plt.axis("off"); plt.tight_layout(); plt.savefig(f"{OUT}/grafo_financiamento_publico.png", dpi=140, bbox_inches="tight"); plt.close()
    print(f"\npico Tier-1 somado: R$ {inv['pico'].sum()/1e6:,.1f} mi | entes no grafo: {inv.height}")
    print("-> dair_distribuicao_temporal.png + grafo_financiamento_publico.png/.graphml")


if __name__ == "__main__":
    main()
