from collections import defaultdict
import networkx as nx

def _id_socio(socio: dict) -> str:

    identificador = socio.get("identificador_de_socio")
    cpf_cnpj = "".join(filter(str.isdigit, socio.get("cnpj_cpf_do_socio", "")))

    if identificador == 1 and len(cpf_cnpj) == 14:
        return cpf_cnpj
    return socio.get("nome_socio", cpf_cnpj or "DESCONHECIDO")

def _tipo_socio(socio: dict) -> str:
    return "empresa" if socio.get("identificador_de_socio") == 1 else "pessoa"

def construir_grafo(dados: dict[str, dict]) -> nx.DiGraph:

    grafo = nx.DiGraph()

    for cnpj, info in dados.items():
        grafo.add_node(
            cnpj,
            label=info.get("razao_social", cnpj),
            tipo="empresa",
            situacao=info.get("descricao_situacao_cadastral", ""),
            capital_social=info.get("capital_social", 0),
            uf=info.get("uf", ""),
            cnae=info.get("cnae_fiscal_descricao", ""),
        )

        for socio in info.get("qsa", []):
            socio_id = _id_socio(socio)
            tipo = _tipo_socio(socio)

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
    projecao = nx.Graph()

    pessoas_por_empresa: dict[str, list[str]] = defaultdict(list)
    for socio, empresa in grafo.edges():
        if grafo.nodes[socio].get("tipo") == "pessoa":
            pessoas_por_empresa[empresa].append(socio)

    for empresa, pessoas in pessoas_por_empresa.items():
        nome_empresa = grafo.nodes[empresa].get("label", empresa)

        for pessoa in pessoas:
            if not projecao.has_node(pessoa):
                projecao.add_node(
                    pessoa,
                    label=grafo.nodes[pessoa].get("label", pessoa),
                    tipo="pessoa",
                )

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
    if node_id not in grafo:
        raise ValueError(f"Nó '{node_id}' não existe no grafo")

    return nx.ego_graph(grafo, node_id, radius=raio, undirected=True)
