from coleta.receita import carregar_ou_coletar
from grafo.societario import construir_grafo, projetar_pessoas
from grafo.analise import analisar_componentes, calcular_metricas, inspecionar_no
from grafo.visualizacao import pyvis_pessoas, pyvis_societario


def main() -> None:
    dados = carregar_ou_coletar()
    grafo = construir_grafo(dados)

    df_metricas = calcular_metricas(grafo)
    print("\n[PIPELINE] Top 20 por betweenness:")
    print(df_metricas.head(20).to_string(index=False))

    analisar_componentes(grafo)
    inspecionar_no(grafo, "VORCARO")
    inspecionar_no(grafo, "VIKING")

    pyvis_societario(grafo, output="grafo_master.html")
    projecao_pessoas = projetar_pessoas(grafo)
    pyvis_pessoas(projecao_pessoas, output="grafo_pessoas.html")


if __name__ == "__main__":
    main()
