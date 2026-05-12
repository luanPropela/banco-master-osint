"""
Ponto de entrada do projeto BancoMaster OSINT.

Orquestra o pipeline completo:
    coleta → construção do grafo → métricas → análise → visualização.

Basta executar `python main.py`. Se o cache `data/cnpjs.json` não
existir, a coleta será disparada automaticamente.
"""

from analise import analisar_componentes, calcular_metricas, inspecionar_no
from coleta import carregar_ou_coletar
from grafo import construir_grafo, projetar_pessoas
from visualizacao import pyvis_pessoas, pyvis_societario


def main() -> None:
    # 1. Coleta (cache em disco se já existir).
    dados = carregar_ou_coletar()

    # 2. Constrói o grafo direcionado sócio → empresa.
    grafo = construir_grafo(dados)

    # 3. Calcula métricas e imprime as 20 maiores betweenness.
    #    A função também persiste a betweenness nos nós, o que o PyVis
    #    consome adiante para escalar o tamanho dos círculos.
    df_metricas = calcular_metricas(grafo)
    print("\n[MAIN] Top 20 por betweenness:")
    print(df_metricas.head(20).to_string(index=False))

    # 4. Análise estrutural — quais ilhas existem, ex.: Will Bank separado.
    analisar_componentes(grafo)

    # 5. Zoom em nós de interesse jornalístico.
    inspecionar_no(grafo, "VORCARO")
    inspecionar_no(grafo, "VIKING")

    # 6. Visualizações HTML — abrem no browser ao final.
    pyvis_societario(grafo, output="grafo_master.html")

    projecao_pessoas = projetar_pessoas(grafo)
    pyvis_pessoas(projecao_pessoas, output="grafo_pessoas.html")


if __name__ == "__main__":
    main()
