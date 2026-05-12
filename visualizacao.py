"""
Camada de visualização — HTML interativo (PyVis) e PNG estático (Matplotlib).

Nenhuma função aqui calcula métricas; espera-se que os atributos
relevantes (em especial `betweenness`) já estejam persistidos nos nós
pelo módulo `analise`. Isso mantém a separação de responsabilidades:
analise = números, visualizacao = pixels.
"""

import os
import webbrowser

import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network

from config import BG_GRAFO, COR_EMPRESA, COR_PESSOA

CORES_POR_TIPO = {"empresa": COR_EMPRESA, "pessoa": COR_PESSOA}


def _abrir_no_browser(caminho_html: str) -> None:
    """Abre o arquivo HTML gerado no navegador padrão do sistema."""
    caminho_absoluto = os.path.abspath(caminho_html)
    webbrowser.open(f"file:///{caminho_absoluto}")
    print(f"[VIZ] aberto: {caminho_absoluto}")


def _injetar_css_body(html: str) -> str:
    """Remove margens padrão do PyVis para o grafo ocupar a tela inteira."""
    return html.replace(
        "<body>",
        f"<body style='margin:0; padding:0; overflow:hidden; background:{BG_GRAFO};'>",
    )


def _salvar_html(net: Network, output: str) -> None:
    """Gera o HTML do PyVis, ajusta o CSS e grava no disco."""
    html = _injetar_css_body(net.generate_html())
    with open(output, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)


def pyvis_societario(grafo: nx.DiGraph, output: str = "grafo_master.html") -> None:
    """
    Gera HTML interativo do grafo completo sócio → empresa.

    O tamanho do nó é proporcional ao betweenness (já calculado por
    `analise.calcular_metricas`) — quanto maior, mais "central" no fluxo
    de relações. Empresas são azuis, pessoas são vermelhas.
    """
    net = Network(
        height="100vh",
        width="100%",
        bgcolor=BG_GRAFO,
        font_color="white",
        directed=True,
        cdn_resources="remote",
        notebook=False,
    )

    # Layout force-directed com gravidade negativa = nós se repelem,
    # produzindo um desenho mais "aberto" e legível.
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=150,
        spring_strength=0.05,
        damping=0.9,
    )

    for node_id in grafo.nodes:
        atributos = grafo.nodes[node_id]
        betweenness = atributos.get("betweenness", 0)
        # Escala 10..60 para o tamanho — limita os extremos para não
        # quebrar o layout em casos com betweenness muito alta.
        tamanho = max(10, min(60, 10 + betweenness * 500))

        tooltip = (
            f"<b>{atributos.get('label', node_id)}</b><br>"
            f"Tipo: {atributos.get('tipo', '-')}<br>"
            f"Situação: {atributos.get('situacao', '-')}<br>"
            f"UF: {atributos.get('uf', '-')}<br>"
            f"In: {grafo.in_degree(node_id)} | Out: {grafo.out_degree(node_id)}<br>"
            f"Betweenness: {round(betweenness, 5)}"
        )

        net.add_node(
            node_id,
            label=str(atributos.get("label", node_id))[:40],
            color=CORES_POR_TIPO.get(atributos.get("tipo", "empresa"), "#aaa"),
            size=tamanho,
            title=tooltip,
        )

    for origem, destino, dados_aresta in grafo.edges(data=True):
        qualificacao = dados_aresta.get("qualificacao", "")
        data_entrada = dados_aresta.get("data_entrada", "")
        net.add_edge(
            origem,
            destino,
            # `label` aparece direto sobre a aresta; `title` é o hover.
            label=qualificacao,
            title=f"{qualificacao} | entrada: {data_entrada}",
            arrows="to",
            color="#555555",
        )

    _salvar_html(net, output)
    _abrir_no_browser(output)


def pyvis_pessoas(projecao: nx.Graph, output: str = "grafo_pessoas.html") -> None:
    """
    Gera HTML da projeção pessoa-pessoa (saída de `grafo.projetar_pessoas`).

    A espessura da aresta cresce com o número de empresas em comum e o
    tooltip lista esses nomes — uma aresta "grossa" entre dois nomes é
    sinal forte de aliança recorrente.
    """
    net = Network(
        height="100vh",
        width="100%",
        bgcolor=BG_GRAFO,
        font_color="white",
        directed=False,
        cdn_resources="remote",
        notebook=False,
    )

    net.barnes_hut(
        gravity=-6000,
        central_gravity=0.4,
        spring_length=120,
        spring_strength=0.06,
        damping=0.9,
    )

    for node_id in projecao.nodes:
        atributos = projecao.nodes[node_id]
        net.add_node(
            node_id,
            label=str(atributos.get("label", node_id))[:40],
            color=COR_PESSOA,
            size=15,
            title=f"<b>{atributos.get('label', node_id)}</b>",
        )

    for pessoa_a, pessoa_b, dados_aresta in projecao.edges(data=True):
        peso = dados_aresta.get("peso", 1)
        empresas = dados_aresta.get("empresas", [])
        tooltip = (
            f"<b>{peso} empresa(s) em comum</b><br>"
            + "<br>".join(empresas)
        )
        net.add_edge(
            pessoa_a,
            pessoa_b,
            value=peso,           # PyVis usa `value` para escalar espessura
            width=1 + peso,
            title=tooltip,
            color="#888888",
        )

    _salvar_html(net, output)
    _abrir_no_browser(output)


def matplotlib_estatico(grafo: nx.DiGraph, output: str = "data/grafo.png") -> None:
    """
    Renderiza uma imagem PNG estática do grafo para documentação.

    Não pretende competir em legibilidade com o PyVis — serve para README,
    relatórios em PDF e qualquer canal que não execute HTML interativo.
    """
    print(f"[VIZ] gerando PNG estático em {output}...")

    plt.figure(figsize=(20, 14))
    posicoes = nx.spring_layout(grafo, k=0.5, iterations=50, seed=42)

    cores_nos = [
        CORES_POR_TIPO.get(grafo.nodes[node].get("tipo", "empresa"), "#aaa")
        for node in grafo.nodes
    ]

    nx.draw_networkx_nodes(grafo, posicoes, node_color=cores_nos, node_size=80, alpha=0.85)
    nx.draw_networkx_edges(grafo, posicoes, edge_color="#444", arrows=True, alpha=0.5)

    # Rotula apenas os nós com maior betweenness para evitar poluição visual.
    top_labels = sorted(
        grafo.nodes,
        key=lambda n: grafo.nodes[n].get("betweenness", 0),
        reverse=True,
    )[:20]
    labels_top = {
        node: str(grafo.nodes[node].get("label", node))[:25]
        for node in top_labels
    }
    nx.draw_networkx_labels(grafo, posicoes, labels=labels_top, font_size=8, font_color="white")

    plt.gca().set_facecolor(BG_GRAFO)
    plt.gcf().set_facecolor(BG_GRAFO)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output, dpi=150, facecolor=BG_GRAFO, bbox_inches="tight")
    plt.close()

    print(f"[VIZ] salvo: {output}")
