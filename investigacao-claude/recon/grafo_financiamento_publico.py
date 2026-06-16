"""Grafo de financiamento público: RPPS (Tier-1) --aportou_em--> BANCO MASTER --cessão--> SDG II --> devedores.
Lê o resumo do DAIR (polars), monta DiGraph (networkx), exporta GraphML + PNG (matplotlib)."""
import sys
import polars as pl
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = "investigacao-claude/dados"
RESUMO = f"{OUT}/dair_follow_the_money_resumo.csv"
MASTER = "BANCO MASTER"


def main():
    res = pl.read_csv(RESUMO)
    t1 = res.filter((pl.col("tier") == "Tier1_LF_Master") & (pl.col("pico_valor") > 0)).sort("pico_valor", descending=True)

    G = nx.DiGraph()
    G.add_node(MASTER, layer=1, tipo="banco", valor=0)
    # lado-passivo: RPPS -> Master
    for r in t1.iter_rows(named=True):
        nome = f"{r['Ente']}/{r['UF']}"
        G.add_node(nome, layer=0, tipo="rpps", valor=r["pico_valor"], pct=r["pct_pico"],
                   congelou=bool(r["congelou_na_liquidacao"]))
        G.add_edge(nome, MASTER, rel="aportou_em", valor=r["pico_valor"],
                   pct_carteira=r["pct_pico"], instrumento="Letra Financeira")
    # lado-ativo: Master -> SDG II -> devedores (da reconstrução)
    G.add_node("SDG II FIDC", layer=2, tipo="fidc", valor=3.36e9)
    G.add_edge(MASTER, "SDG II FIDC", rel="cessao_credito", valor=1.129e9, detalhe="2 cessões 19/12/2024")
    for dev, val in [("Lormont (Tanure)", 5.97e8), ("Banvox (debênture)", 3.80e8), ("Super Empreend.", 2.2e7)]:
        G.add_node(dev, layer=3, tipo="devedor", valor=val)
        G.add_edge("SDG II FIDC", dev, rel="credito_a_receber", valor=val)

    nx.write_graphml(G, f"{OUT}/grafo_financiamento_publico.graphml")

    # --- desenho ---
    pos = nx.multipartite_layout(G, subset_key="layer", scale=2.4)
    plt.figure(figsize=(17, 11))
    cor = {"rpps": "#BAD9F5", "banco": "#0C253A", "fidc": "#C0392B", "devedor": "#C0B394"}
    sizes = [max(500, (G.nodes[n].get("valor", 0) / 1e6) * 9 + 500) for n in G.nodes]
    cores = [cor[G.nodes[n]["tipo"]] for n in G.nodes]
    ew = [max(0.6, (d["valor"] / 1e6) * 0.03) for *_, d in G.edges(data=True)]
    ecor = ["#56666F" if d["rel"] == "aportou_em" else "#C0392B" for *_, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, width=ew, edge_color=ecor, alpha=0.6, arrowsize=12)
    nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color=cores, edgecolors="#0C253A", linewidths=0.6)
    labels = {n: (n if G.nodes[n]["tipo"] != "rpps"
                  else f"{n}\nR$ {G.nodes[n]['valor']/1e6:.0f} mi · {G.nodes[n]['pct']:.1f}%") for n in G.nodes}
    nx.draw_networkx_labels(G, pos, labels, font_size=7, font_color="#0C253A")
    plt.title("Financiamento público do Banco Master (aportou_em) → ocultação no SDG II\n"
              "Esquerda: RPPS que compraram Letra Financeira do Master · Direita: onde o crédito podre foi parar",
              fontsize=12, color="#0C253A")
    plt.axis("off"); plt.tight_layout()
    plt.savefig(f"{OUT}/grafo_financiamento_publico.png", dpi=140, bbox_inches="tight")
    print(f"nós: {G.number_of_nodes()} | arestas: {G.number_of_edges()}")
    print(f"RPPS Tier-1 no grafo: {t1.height} | pico somado R$ {t1['pico_valor'].sum()/1e6:,.1f} mi")
    print(f"-> {OUT}/grafo_financiamento_publico.graphml + .png")


if __name__ == "__main__":
    main()
