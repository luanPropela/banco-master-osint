import io
import json
import math
import os
import time
import webbrowser
from pathlib import Path

import networkx as nx
import pandas as pd
import requests
from pyvis.network import Network

CNPJS_MASTER: dict[str, str] = {
    "33923798000100": "Banco Master S/A",
    "33884941000194": "Banco Master Múltiplo S/A",
    "09526594000143": "Banco Master de Investimento S/A",
    "58497702000102": "Banco Letsbank S/A",
    "07875796000175": "Viking Participações Ltda",
    "33886862000112": "Master S/A Corretora CCTVM",
}

CACHE_B2B = Path("data/fundos_b2b.json")
URL_CAD_FI = "https://dados.cvm.gov.br/dados/FI/CAD/DADOS/cad_fi.csv"
URL_CAD_FII_CANDIDATOS = [
    "https://dados.cvm.gov.br/dados/FII/CAD/DADOS/cad_fii.csv",
    "https://dados.cvm.gov.br/dados/FII/CAD/DADOS/inf_cadastral_fii.csv",
]
URL_MINHA_RECEITA = "https://minhareceita.org/{cnpj}"
TIMEOUT_HTTP = 60
BG_GRAFO = "#1a1a2e"

TIPOS_NO = {
    "banco":     {"cor": "#4A90D9", "forma": "dot"},
    "fundo":     {"cor": "#5BA85A", "forma": "diamond"},
    "gestora":   {"cor": "#E8A05D", "forma": "square"},
    "corretora": {"cor": "#9B59B6", "forma": "dot"},
    "pessoa":    {"cor": "#E85D5D", "forma": "dot"},
}
TIPOS_ARESTA = {
    "administra": {"cor": "#4A90D9", "label": "administra"},
    "gere":       {"cor": "#E8A05D", "label": "gere"},
    "custodia":   {"cor": "#9B59B6", "label": "custodia"},
    "controla":   {"cor": "#E85D5D", "label": "controla"},
    "e_socio_de": {"cor": "#888888", "label": "sócio"},
}

def _norm_cnpj(valor) -> str:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return ""
    return "".join(filter(str.isdigit, str(valor)))

def _get(url: str) -> requests.Response | None:
    try:
        resposta = requests.get(url, timeout=TIMEOUT_HTTP)
        if resposta.status_code == 200:
            return resposta
        print(f"[B2B] HTTP {resposta.status_code} em {url}")
    except requests.RequestException as erro:
        print(f"[B2B] falha em {url}: {erro}")
    return None

def _ler_csv(conteudo: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(
            io.BytesIO(conteudo),
            sep=";", encoding="latin-1", dtype=str,
            on_bad_lines="skip", low_memory=False,
        )
    except Exception as erro:
        print(f"[B2B] erro ao parsear CSV: {erro}")
        return pd.DataFrame()

def baixar_cadastro_fi() -> pd.DataFrame:
    print("[B2B] baixando cad_fi da CVM...")
    resposta = _get(URL_CAD_FI)
    df = _ler_csv(resposta.content) if resposta else pd.DataFrame()
    if not df.empty:
        print(f"[B2B] cad_fi: {len(df):,} linhas")
    return df

def baixar_cadastro_fii() -> pd.DataFrame:
    for url in URL_CAD_FII_CANDIDATOS:
        print(f"[B2B] tentando FII: {url}")
        resposta = _get(url)
        if resposta:
            df = _ler_csv(resposta.content)
            if not df.empty:
                print(f"[B2B] cad_fii: {len(df):,} linhas")
                return df
    print("[B2B] cadastro FII indisponível — seguindo só com FI")
    return pd.DataFrame()

COLUNAS_PAPEL = ["CNPJ_ADMIN", "CPF_CNPJ_GESTOR", "CNPJ_CUSTODIANTE",
                 "CNPJ_CONTROLADOR", "CNPJ_ADMINISTRADOR"]

def filtrar_fundos_master(df: pd.DataFrame, cnpjs_master: dict[str, str]) -> pd.DataFrame:
    if df.empty:
        return df
    existentes = [coluna for coluna in COLUNAS_PAPEL if coluna in df.columns]
    if not existentes:
        print("[B2B] CSV sem colunas de papel — não filtrável")
        return pd.DataFrame()
    chaves = set(cnpjs_master.keys())
    mascara = pd.Series(False, index=df.index)
    for coluna in existentes:
        mascara |= df[coluna].apply(_norm_cnpj).isin(chaves)
    filtrado = df[mascara].copy()
    print(f"[B2B] fundos com vínculo Master: {len(filtrado)}")
    return filtrado

def consultar_qsa(cnpj: str) -> dict | None:
    cnpj_limpo = _norm_cnpj(cnpj)
    if len(cnpj_limpo) != 14:
        return None
    resposta = _get(URL_MINHA_RECEITA.format(cnpj=cnpj_limpo))
    try:
        return resposta.json() if resposta else None
    except ValueError:
        return None

def carregar_ou_coletar(forcar: bool = False) -> dict:
    if CACHE_B2B.exists() and not forcar:
        print(f"[B2B] usando cache: {CACHE_B2B}")
        with CACHE_B2B.open(encoding="utf-8") as arquivo:
            return json.load(arquivo)

    print("[B2B] coletando dados frescos")
    df_fi = filtrar_fundos_master(baixar_cadastro_fi(), CNPJS_MASTER)
    df_fii = filtrar_fundos_master(baixar_cadastro_fii(), CNPJS_MASTER)

    qsa: dict[str, dict] = {}
    for cnpj, nome in CNPJS_MASTER.items():
        print(f"[B2B] QSA de {nome} ({cnpj})")
        dados = consultar_qsa(cnpj)
        if dados:
            qsa[cnpj] = dados
        time.sleep(0.8)

    def _para_dict(df: pd.DataFrame) -> list[dict]:
        return df.fillna("").astype(str).to_dict(orient="records") if not df.empty else []

    pacote = {"fundos_fi": _para_dict(df_fi), "fundos_fii": _para_dict(df_fii), "qsa": qsa}
    CACHE_B2B.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_B2B.open("w", encoding="utf-8") as arquivo:
        json.dump(pacote, arquivo, ensure_ascii=False, indent=2)
    print(f"[B2B] cache salvo em {CACHE_B2B}")
    return pacote

def _add_no(grafo: nx.DiGraph, node_id: str, **atributos) -> None:
    if grafo.has_node(node_id):
        for chave, valor in atributos.items():
            if valor and not grafo.nodes[node_id].get(chave):
                grafo.nodes[node_id][chave] = valor
    else:
        grafo.add_node(node_id, **atributos)

def _tipo_master(nome: str) -> str:
    nome_upper = (nome or "").upper()
    if "CORRETORA" in nome_upper or "CCTVM" in nome_upper:
        return "corretora"
    return "banco"

PAPEIS_FUNDO = [

    ("CNPJ_ADMIN",         "ADMIN",            "administra", "corretora"),
    ("CNPJ_ADMINISTRADOR", "NM_ADMINISTRADOR", "administra", "corretora"),
    ("CPF_CNPJ_GESTOR",    "GESTOR",           "gere",       "gestora"),
    ("CNPJ_CUSTODIANTE",   "CUSTODIANTE",      "custodia",   "corretora"),
    ("CNPJ_CONTROLADOR",   "CONTROLADOR",      "controla",   "banco"),
]

def _processar_linha_fundo(grafo: nx.DiGraph, linha: dict) -> None:
    cnpj_fundo = _norm_cnpj(linha.get("CNPJ_FUNDO", ""))
    if not cnpj_fundo:
        return
    nome_fundo = linha.get("DENOM_SOCIAL") or linha.get("NM_FUNDO") or cnpj_fundo
    _add_no(grafo, cnpj_fundo, label=nome_fundo, tipo="fundo",
            subtipo=linha.get("TP_FUNDO", ""), situacao=linha.get("SIT", ""),
            pl=linha.get("VL_PATRIM_LIQ", ""))

    for col_cnpj, col_nome, tipo_aresta, tipo_no in PAPEIS_FUNDO:
        cnpj_papel, nome_papel = linha.get(col_cnpj), linha.get(col_nome) or linha.get("NM_GESTOR")
        cnpj_papel = _norm_cnpj(cnpj_papel)
        if not cnpj_papel:
            continue
        if cnpj_papel in CNPJS_MASTER:
            nome_papel = CNPJS_MASTER[cnpj_papel]
            tipo_no = _tipo_master(nome_papel)
        _add_no(grafo, cnpj_papel, label=nome_papel or cnpj_papel, tipo=tipo_no)
        grafo.add_edge(cnpj_papel, cnpj_fundo, tipo=tipo_aresta)

def construir_grafo_b2b(dados: dict) -> nx.DiGraph:
    grafo = nx.DiGraph()

    for cnpj, nome in CNPJS_MASTER.items():
        _add_no(grafo, cnpj, label=nome, tipo=_tipo_master(nome))

    for linha in dados.get("fundos_fi", []):
        _processar_linha_fundo(grafo, linha)
    for linha in dados.get("fundos_fii", []):
        _processar_linha_fundo(grafo, linha)

    for cnpj_pj, info_pj in (dados.get("qsa") or {}).items():
        for socio in info_pj.get("qsa", []) or []:

            if socio.get("identificador_de_socio") != 2:
                continue
            nome = socio.get("nome_socio") or "DESCONHECIDO"
            _add_no(grafo, nome, label=nome, tipo="pessoa",
                    faixa_etaria=socio.get("faixa_etaria", ""))
            grafo.add_edge(nome, cnpj_pj,
                           tipo="e_socio_de",
                           qualificacao=socio.get("qualificacao_socio", ""))
    return grafo

def adicionar_macam_manual(grafo: nx.DiGraph) -> nx.DiGraph:
    cnpj_macam, cnpj_corretora, bluemac = "16685929000131", "33886862000112", "BLUEMAC"
    macam = {
        "label": "MACAM Shopping FII", "tipo": "fundo", "subtipo": "FII",
        "segmento": "Shoppings", "pl": 472793957.87,
        "pl_jan25": 478285846.31, "pl_dez25": 472793957.87,
        "variacao_pl": -5491888.44, "cotistas_jan25": 28, "cotistas_dez25": 130,
        "vencimento": "2026-09-27", "taxa_admin_devida": 16318815.80,
        "passivo_total_dez25": 21439252.34, "isin": "BRFRLSCTF000",
        "rentabilidade_acum_2025": "negativa todos os meses",
        "situacao": "EM FUNCIONAMENTO NORMAL",
        "alerta": "Cotistas triplicaram após liquidação do administrador. Vence set/2026.",
    }
    _add_no(grafo, cnpj_macam, **macam)
    grafo.nodes[cnpj_macam].update(macam)
    _add_no(grafo, cnpj_corretora, label="Master S/A Corretora CCTVM", tipo="corretora")
    _add_no(grafo, bluemac, label="Bluemac Asset Management", tipo="gestora")

    grafo.add_edge(cnpj_corretora, cnpj_macam,
                   tipo="administra", extra="administra + custodia")
    grafo.add_edge(bluemac, cnpj_macam, tipo="gere")
    return grafo

def _pl_numero(atributos: dict) -> float:
    try:    return float(atributos.get("pl") or 0)
    except (TypeError, ValueError): return 0.0

def _tooltip(node_id: str, atributos: dict, grafo: nx.DiGraph) -> str:
    linhas = [f"<b>{atributos.get('label', node_id)}</b>"]
    for chave in ("tipo", "subtipo", "segmento", "situacao", "alerta"):
        if atributos.get(chave):
            linhas.append(f"{chave}: {atributos[chave]}")
    pl_num = _pl_numero(atributos)
    if pl_num:
        linhas.append(f"PL: R$ {pl_num:,.2f}")
    linhas.append(f"in={grafo.in_degree(node_id)} out={grafo.out_degree(node_id)}")
    return "<br>".join(linhas)

def _tamanho(atributos: dict, grau: int) -> int:
    pl_num = _pl_numero(atributos)
    if pl_num > 0:
        return int(max(15, min(55, 8 + math.log10(pl_num) * 4)))
    return int(max(12, min(40, 12 + grau * 3)))

def _legenda_html() -> str:
    itens = "".join(
        f'<div><span style="display:inline-block;width:12px;height:12px;'
        f'background:{p["cor"]};margin-right:6px;border-radius:50%;"></span>{t}</div>'
        for t, p in TIPOS_NO.items())
    return ('<div style="position:fixed;top:10px;right:10px;background:rgba(0,0,0,0.7);'
            'color:white;padding:10px;border-radius:6px;font-family:sans-serif;'
            f'font-size:12px;z-index:9999;"><b>Legenda</b>{itens}</div>')

def construir_pyvis_b2b(grafo: nx.DiGraph, output: str = "grafo_b2b.html") -> Network:
    net = Network(height="100vh", width="100%", bgcolor=BG_GRAFO,
                  font_color="white", directed=True,
                  cdn_resources="remote", notebook=False)
    net.barnes_hut(gravity=-7000, central_gravity=0.3,
                   spring_length=180, spring_strength=0.04, damping=0.9)

    for node_id in grafo.nodes:
        atributos = grafo.nodes[node_id]
        estilo = TIPOS_NO.get(atributos.get("tipo", "banco"), TIPOS_NO["banco"])
        grau = grafo.in_degree(node_id) + grafo.out_degree(node_id)
        net.add_node(node_id, label=str(atributos.get("label", node_id))[:42],
                     color=estilo["cor"], shape=estilo["forma"],
                     size=_tamanho(atributos, grau),
                     title=_tooltip(node_id, atributos, grafo))

    for origem, destino, dados_aresta in grafo.edges(data=True):
        estilo = TIPOS_ARESTA.get(dados_aresta.get("tipo", "administra"),
                                  TIPOS_ARESTA["administra"])
        label = dados_aresta.get("extra") or estilo["label"]
        net.add_edge(origem, destino, label=label, title=label,
                     arrows="to", color=estilo["cor"])

    html = net.generate_html().replace(
        "<body>",
        f"<body style='margin:0;padding:0;overflow:hidden;background:{BG_GRAFO};'>")
    html = html.replace("<body", _legenda_html() + "<body", 1)
    Path(output).write_text(html, encoding="utf-8")
    caminho = os.path.abspath(output)
    try:
        webbrowser.open(f"file:///{caminho}")
    except Exception:
        pass
    print(f"[B2B] HTML salvo: {caminho}")
    return net

def _contar_por_chave(itens, chave_fn) -> dict:
    contagem: dict = {}
    for item in itens:
        chave = chave_fn(item)
        contagem[chave] = contagem.get(chave, 0) + 1
    return dict(sorted(contagem.items(), key=lambda i: -i[1]))

def resumo_b2b(grafo: nx.DiGraph) -> None:
    print(f"\n[B2B] === RESUMO ===")
    print(f"nós: {grafo.number_of_nodes()} | arestas: {grafo.number_of_edges()}")
    print("nós por tipo:",
          _contar_por_chave(grafo.nodes, lambda n: grafo.nodes[n].get("tipo", "?")))
    print("arestas por tipo:",
          _contar_por_chave(grafo.edges(data=True), lambda e: e[2].get("tipo", "?")))

    grau = {n: grafo.in_degree(n) + grafo.out_degree(n) for n in grafo.nodes}
    print("top hubs:")
    for node_id in sorted(grau, key=grau.get, reverse=True)[:10]:
        print(f"  {grau[node_id]:>3} — {grafo.nodes[node_id].get('label', node_id)}")

    def _pl(node_id):
        try:    return float(grafo.nodes[node_id].get("pl") or 0)
        except (TypeError, ValueError): return 0.0
    total_pl = sum(_pl(n) for n in grafo.nodes)
    print(f"PL total (nós com PL conhecido): R$ {total_pl:,.2f}")

if __name__ == "__main__":
    dados = carregar_ou_coletar()
    grafo = construir_grafo_b2b(dados)
    grafo = adicionar_macam_manual(grafo)
    resumo_b2b(grafo)
    construir_pyvis_b2b(grafo)
