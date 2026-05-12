"""
Construção dos grafos NetworkX a partir dos dados coletados.

Dois grafos principais são produzidos:

* `construir_grafo` — grafo direcionado (DiGraph) sócio → empresa,
  representando fielmente o QSA da Receita. Empresas e pessoas são nós
  distintos, tipados pelo atributo `tipo`.
* `projetar_pessoas` — projeção não-direcionada onde duas pessoas se
  ligam se aparecem no QSA da mesma empresa. Útil para enxergar
  "panelinhas" societárias diretamente entre pessoas físicas.
"""

from collections import defaultdict

import networkx as nx


def _id_socio(socio: dict) -> str:
    """
    Retorna um identificador estável para o sócio.

    Para pessoas jurídicas usa o CNPJ (14 dígitos). Para pessoas físicas,
    o CPF vem mascarado (`***xxx**`), então o nome é o identificador
    mais confiável — mesmo padrão usado por reportagens OSINT da área.
    """
    identificador = socio.get("identificador_de_socio")
    cpf_cnpj = "".join(filter(str.isdigit, socio.get("cnpj_cpf_do_socio", "")))

    if identificador == 1 and len(cpf_cnpj) == 14:
        return cpf_cnpj
    return socio.get("nome_socio", cpf_cnpj or "DESCONHECIDO")


def _tipo_socio(socio: dict) -> str:
    """Mapeia o `identificador_de_socio` da Receita para 'empresa' ou 'pessoa'."""
    return "empresa" if socio.get("identificador_de_socio") == 1 else "pessoa"


def construir_grafo(dados: dict[str, dict]) -> nx.DiGraph:
    """
    Monta o grafo direcionado sócio → empresa.

    Atributos persistidos nos nós e arestas alimentam tanto a análise
    (graus, betweenness) quanto a visualização (tooltips do PyVis).
    """
    grafo = nx.DiGraph()

    for cnpj, info in dados.items():
        # Nó empresa — atributos vindos do cadastro da Receita.
        grafo.add_node(
            cnpj,
            label=info.get("razao_social", cnpj),
            tipo="empresa",
            situacao=info.get("descricao_situacao_cadastral", ""),
            capital_social=info.get("capital_social", 0),
            uf=info.get("uf", ""),
            cnae=info.get("cnae_fiscal_descricao", ""),
        )

        # Cada sócio vira um nó (pessoa ou empresa) com aresta apontando para a empresa.
        for socio in info.get("qsa", []):
            socio_id = _id_socio(socio)
            tipo = _tipo_socio(socio)

            # Evita sobrescrever atributos ricos de uma empresa que já está
            # como nó completo (ex.: seed conhecida) por dados vazios do QSA.
            if not grafo.has_node(socio_id):
                grafo.add_node(
                    socio_id,
                    label=socio.get("nome_socio", socio_id),
                    tipo=tipo,
                    situacao="",
                    faixa_etaria=socio.get("faixa_etaria", ""),
                )

            grafo.add_edge(
                socio_id,
                cnpj,
                qualificacao=socio.get("qualificacao_socio", ""),
                data_entrada=socio.get("data_entrada_sociedade", ""),
            )

    return grafo


def projetar_pessoas(grafo: nx.DiGraph) -> nx.Graph:
    """
    Projeta o grafo bipartido em uma rede pessoa-pessoa.

    Duas pessoas ficam conectadas se compartilham ao menos uma empresa
    no QSA. O peso da aresta indica quantas empresas em comum elas têm e
    o atributo `empresas` lista os nomes — base para identificar grupos
    que se movem juntos por várias razões sociais.
    """
    projecao = nx.Graph()

    # Para cada empresa, junta a lista de pessoas físicas que apontam para ela.
    pessoas_por_empresa: dict[str, list[str]] = defaultdict(list)
    for socio, empresa in grafo.edges():
        if grafo.nodes[socio].get("tipo") == "pessoa":
            pessoas_por_empresa[empresa].append(socio)

    # Adiciona cada pessoa como nó na projeção, copiando atributos relevantes.
    for empresa, pessoas in pessoas_por_empresa.items():
        nome_empresa = grafo.nodes[empresa].get("label", empresa)

        for pessoa in pessoas:
            if not projecao.has_node(pessoa):
                projecao.add_node(
                    pessoa,
                    label=grafo.nodes[pessoa].get("label", pessoa),
                    tipo="pessoa",
                )

        # Liga todas as duplas (combinação 2 a 2) de pessoas dessa empresa.
        for i, pessoa_a in enumerate(pessoas):
            for pessoa_b in pessoas[i + 1:]:
                if projecao.has_edge(pessoa_a, pessoa_b):
                    dados_aresta = projecao[pessoa_a][pessoa_b]
                    dados_aresta["peso"] += 1
                    dados_aresta["empresas"].append(nome_empresa)
                else:
                    projecao.add_edge(
                        pessoa_a,
                        pessoa_b,
                        peso=1,
                        empresas=[nome_empresa],
                    )

    return projecao


def ego_subgrafo(grafo: nx.DiGraph, node_id: str, raio: int = 1) -> nx.DiGraph:
    """
    Devolve o subgrafo composto por um nó central e sua vizinhança.

    `raio=1` traz vizinhos imediatos; `raio=2` traz vizinhos dos vizinhos, e
    assim por diante. Útil para isolar um personagem (ex.: VORCARO) sem
    o ruído do grafo completo. A direção das arestas é ignorada na
    expansão para captar tanto sócios quanto empresas controladas.
    """
    if node_id not in grafo:
        raise ValueError(f"Nó '{node_id}' não existe no grafo")

    return nx.ego_graph(grafo, node_id, radius=raio, undirected=True)
