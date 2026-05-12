"""
Coleta de dados da API pública Minha Receita (https://minhareceita.org).

A API encapsula o cadastro QSA (Quadro de Sócios e Administradores) da
Receita Federal. Este módulo faz uma busca em largura (BFS) partindo das
sementes definidas em `config.SEEDS` e expande, a cada nível, os sócios
do tipo pessoa jurídica (CNPJ) — sócios pessoa física não são expandidos
porque a Receita mascara o CPF.

Códigos de identificador_de_socio segundo a Receita Federal:
    1 → Pessoa Jurídica (PJ) — possui CNPJ, deve ser expandido pelo BFS
    2 → Pessoa Física    (PF) — CPF mascarado, é folha do grafo
"""

import json
import time
from collections import deque
from pathlib import Path

import requests

from config import CACHE_PATH, DELAY_SEGUNDOS, MAX_DEPTH, SEEDS

API_URL = "https://minhareceita.org/{cnpj}"
TIMEOUT_HTTP = 15


def _so_digitos(texto: str) -> str:
    """Mantém apenas os dígitos numéricos de uma string (remove pontuação)."""
    return "".join(filter(str.isdigit, texto or ""))


def consultar_cnpj(cnpj: str) -> dict | None:
    """
    Consulta um único CNPJ na API Minha Receita.

    Retorna o JSON parseado em caso de sucesso, ou None caso o CNPJ seja
    inválido / a API retorne erro / timeout. Erros são logados, mas nunca
    interrompem a coleta (a API pública é instável e algumas falhas são
    esperadas).
    """
    cnpj_limpo = _so_digitos(cnpj)
    if len(cnpj_limpo) != 14:
        return None

    try:
        resposta = requests.get(API_URL.format(cnpj=cnpj_limpo), timeout=TIMEOUT_HTTP)
        if resposta.status_code == 200:
            return resposta.json()
        print(f"[COLETA] HTTP {resposta.status_code} para {cnpj_limpo}")
    except requests.RequestException as erro:
        print(f"[COLETA] Falha de rede em {cnpj_limpo}: {erro}")
    return None


def coletar(
    seeds: dict[str, str],
    max_depth: int = MAX_DEPTH,
    delay: float = DELAY_SEGUNDOS,
) -> dict[str, dict]:
    """
    Executa BFS a partir das sementes e devolve um dicionário CNPJ → dados.

    A profundidade controla até que nível de sócios PJ o crawler desce. Com
    `max_depth=2`, parte-se das sementes (nível 0), visita-se cada sócio PJ
    delas (nível 1) e ainda os sócios PJ desses (nível 2).
    """
    visitados: dict[str, dict] = {}
    # Fila de tuplas (cnpj, depth). Inicializa com todas as sementes no nível 0.
    fila: deque[tuple[str, int]] = deque((cnpj, 0) for cnpj in seeds.keys())

    while fila:
        cnpj, depth = fila.popleft()

        # Evita reprocessar CNPJs já visitados e respeita o limite de profundidade.
        if cnpj in visitados or depth > max_depth:
            continue

        rotulo = seeds.get(cnpj, cnpj)
        print(f"[COLETA] [depth {depth}] consultando {rotulo} ({cnpj})")

        dados = consultar_cnpj(cnpj)
        if dados is None:
            continue

        visitados[cnpj] = dados
        time.sleep(delay)  # respeita a API pública evitando rate-limit

        # Enfileira sócios PJ (identificador_de_socio == 1) para o próximo nível.
        if depth < max_depth:
            for socio in dados.get("qsa", []):
                if socio.get("identificador_de_socio") != 1:
                    continue
                cnpj_socio = _so_digitos(socio.get("cnpj_cpf_do_socio", ""))
                if len(cnpj_socio) == 14 and cnpj_socio not in visitados:
                    fila.append((cnpj_socio, depth + 1))

    return visitados


def carregar_ou_coletar(forcar: bool = False) -> dict[str, dict]:
    """
    Devolve os dados da coleta usando o cache em disco quando possível.

    Se `forcar=True` ou o arquivo de cache não existir, dispara uma nova
    coleta na API e grava o resultado em `config.CACHE_PATH`. Caso contrário
    apenas lê o JSON em disco — útil para iterar nas etapas seguintes
    (grafo / análise / visualização) sem bater na API a cada execução.
    """
    cache = Path(CACHE_PATH)

    if cache.exists() and not forcar:
        print(f"[COLETA] usando cache local: {cache}")
        with cache.open(encoding="utf-8") as arquivo:
            return json.load(arquivo)

    print("[COLETA] cache ausente ou forçado — coletando da API")
    dados = coletar(SEEDS)

    cache.parent.mkdir(parents=True, exist_ok=True)
    with cache.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

    print(f"[COLETA] {len(dados)} CNPJs salvos em {cache}")
    return dados


if __name__ == "__main__":
    # Execução direta: força recoleta e atualiza o cache.
    carregar_ou_coletar(forcar=True)
