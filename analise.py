"""
Métricas e análises sobre o grafo societário.

Este módulo não desenha nada — apenas calcula números úteis (graus,
betweenness, componentes desconexos, pontos de articulação) e oferece
funções de busca interativa por nome.
"""

import networkx as nx
import pandas as pd


def calcular_metricas(grafo: nx.DiGraph) -> pd.DataFrame:
    """
    Calcula métricas básicas de centralidade e devolve um DataFrame ordenado.

    Importante: a betweenness é calculada na versão não-direcionada do
    grafo. Em DiGraphs com vários componentes fracamente conectados, a
    versão direcionada tende a produzir zeros para a maioria dos nós, o
    que polui a visualização. O valor também é persistido em
    `grafo.nodes[n]['betweenness']` para a visualização escalar tamanho.
    """
    print(f"[ANALISE] nós: {grafo.number_of_nodes()} | arestas: {grafo.number_of_edges()}")
    print("[ANALISE] calculando betweenness centrality...")

    nao_direcionado = grafo.to_undirected()
    betweenness = nx.betweenness_centrality(nao_direcionado, normalized=True)
    nx.set_node_attributes(grafo, betweenness, "betweenness")

    # Monta o DataFrame com uma linha por nó para inspeção em ordem decrescente.
    linhas = [
        {
            "label": grafo.nodes[node].get("label", node),
            "tipo": grafo.nodes[node].get("tipo", ""),
            "in_degree": grafo.in_degree(node),
            "out_degree": grafo.out_degree(node),
            "grau_total": grafo.in_degree(node) + grafo.out_degree(node),
            "betweenness": round(betweenness[node], 5),
        }
        for node in grafo.nodes
    ]

    return (
        pd.DataFrame(linhas)
        .sort_values("betweenness", ascending=False)
        .reset_index(drop=True)
    )


def analisar_componentes(grafo: nx.DiGraph) -> list[set]:
    """
    Lista os componentes fracamente conectados do grafo (e imprime resumo).

    Em uma análise OSINT, blocos desconexos costumam revelar redes
    paralelas — uma "ilha" de empresas pode ser um veículo separado do
    grupo principal e merecer investigação independente.
    """
    componentes = sorted(
        nx.weakly_connected_components(grafo),
        key=len,
        reverse=True,
    )

    print(f"\n[ANALISE] {len(componentes)} componente(s) desconexo(s):")
    for indice, componente in enumerate(componentes[:10], start=1):
        amostra = [
            grafo.nodes[node].get("label", node)
            for node in list(componente)[:3]
        ]
        print(f"  {indice:>2}. {len(componente):>4} nós — ex.: {', '.join(amostra)}")

    return componentes


def pontos_articulacao(grafo: nx.DiGraph) -> list[str]:
    """
    Retorna os nós cuja remoção fragmentaria o grafo (articulation points).

    Em redes societárias, pontos de articulação costumam ser pessoas-chave
    ou holdings que "costuram" subgrupos: removê-las dissolve o caminho
    entre comunidades antes invisíveis.
    """
    pontos = list(nx.articulation_points(grafo.to_undirected()))

    print(f"\n[ANALISE] {len(pontos)} ponto(s) de articulação:")
    for node in pontos[:15]:
        rotulo = grafo.nodes[node].get("label", node)
        tipo = grafo.nodes[node].get("tipo", "")
        print(f"  - [{tipo}] {rotulo}")

    return pontos


def inspecionar_no(grafo: nx.DiGraph, label_busca: str) -> None:
    """
    Imprime os vizinhos e arestas de todo nó cujo label contenha o termo.

    Busca case-insensitive — passe parte do nome ("VORCARO", "VIKING") e
    a função encontra todos os matches. Pensado para uso exploratório no
    terminal, não retorna nada além do print.
    """
    termo = label_busca.upper()
    encontrados = [
        node for node in grafo.nodes
        if termo in str(grafo.nodes[node].get("label", "")).upper()
    ]

    if not encontrados:
        print(f"\n[ANALISE] nenhum nó com '{label_busca}' no label")
        return

    for node in encontrados:
        atributos = grafo.nodes[node]
        print(f"\n[ANALISE] === {atributos.get('label', node)} ===")
        print(f"  tipo:        {atributos.get('tipo', '-')}")
        print(f"  situação:    {atributos.get('situacao', '-')}")
        print(f"  in-degree:   {grafo.in_degree(node)}")
        print(f"  out-degree:  {grafo.out_degree(node)}")
        print(f"  betweenness: {round(atributos.get('betweenness', 0), 5)}")

        # Arestas de saída — empresas das quais este nó é sócio.
        sucessores = list(grafo.successors(node))
        if sucessores:
            print(f"  participa em {len(sucessores)} empresa(s):")
            for empresa in sucessores[:10]:
                dados_aresta = grafo[node][empresa]
                print(
                    f"    → {grafo.nodes[empresa].get('label', empresa)} "
                    f"({dados_aresta.get('qualificacao', '-')})"
                )

        # Arestas de entrada — sócios deste nó (caso seja empresa).
        predecessores = list(grafo.predecessors(node))
        if predecessores:
            print(f"  possui {len(predecessores)} sócio(s):")
            for socio in predecessores[:10]:
                dados_aresta = grafo[socio][node]
                print(
                    f"    ← {grafo.nodes[socio].get('label', socio)} "
                    f"({dados_aresta.get('qualificacao', '-')})"
                )


def caminho_entre(
    grafo: nx.DiGraph,
    origem_label: str,
    destino_label: str,
) -> list[str] | None:
    """
    Encontra o menor caminho entre dois nós identificados pelo label.

    Usa a versão não-direcionada do grafo para não depender da direção
    sócio → empresa. Retorna a lista de labels do caminho ou None se
    origem/destino não forem encontrados ou não houver caminho.
    """
    def _buscar_por_label(termo: str) -> str | None:
        termo_upper = termo.upper()
        for node in grafo.nodes:
            if termo_upper in str(grafo.nodes[node].get("label", "")).upper():
                return node
        return None

    origem = _buscar_por_label(origem_label)
    destino = _buscar_por_label(destino_label)

    if origem is None or destino is None:
        print(f"[ANALISE] não encontrei origem='{origem_label}' ou destino='{destino_label}'")
        return None

    try:
        caminho = nx.shortest_path(grafo.to_undirected(), origem, destino)
    except nx.NetworkXNoPath:
        print(f"[ANALISE] sem caminho entre {origem_label} e {destino_label}")
        return None

    rotulos = [grafo.nodes[n].get("label", n) for n in caminho]
    print(f"\n[ANALISE] caminho {origem_label} → {destino_label}:")
    print("  " + " → ".join(rotulos))
    return rotulos
