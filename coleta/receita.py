import json
import time
from collections import deque
from pathlib import Path

import requests

from config import CACHE_PATH, DELAY_SEGUNDOS, MAX_DEPTH, SEEDS

API_URL = "https://minhareceita.org/{cnpj}"
TIMEOUT_HTTP = 15

def _so_digitos(texto: str) -> str:
    return "".join(filter(str.isdigit, texto or ""))

def consultar_cnpj(cnpj: str) -> dict | None:
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

def _salvar_incremental(cache: Path, visitados: dict[str, dict]) -> None:
    cache.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as arquivo:
        json.dump(visitados, arquivo, ensure_ascii=False, indent=2)
    tmp.replace(cache)

def coletar(
    seeds: dict[str, str],
    max_depth: int = MAX_DEPTH,
    delay: float = DELAY_SEGUNDOS,
    cache_path: str | Path = CACHE_PATH,
) -> dict[str, dict]:
    cache = Path(cache_path)
    visitados: dict[str, dict] = {}
    if cache.exists():
        try:
            with cache.open(encoding="utf-8") as arquivo:
                visitados = json.load(arquivo)
            print(f"[COLETA] retomando de cache parcial: {len(visitados)} CNPJs já coletados")
        except Exception:
            visitados = {}

    fila: deque[tuple[str, int]] = deque((cnpj, 0) for cnpj in seeds.keys())

    while fila:
        cnpj, depth = fila.popleft()

        if cnpj in visitados or depth > max_depth:
            continue

        rotulo = seeds.get(cnpj, cnpj)
        print(f"[COLETA] [depth {depth}] consultando {rotulo} ({cnpj})")

        dados = consultar_cnpj(cnpj)
        if dados is None:
            continue

        visitados[cnpj] = dados
        _salvar_incremental(cache, visitados)
        time.sleep(delay)

        if depth < max_depth:
            for socio in dados.get("qsa", []):
                if socio.get("identificador_de_socio") != 1:
                    continue
                cnpj_socio = _so_digitos(socio.get("cnpj_cpf_do_socio", ""))
                if len(cnpj_socio) == 14 and cnpj_socio not in visitados:
                    fila.append((cnpj_socio, depth + 1))

    return visitados

def carregar_ou_coletar(forcar: bool = False) -> dict[str, dict]:
    cache = Path(CACHE_PATH)

    if cache.exists() and not forcar:
        print(f"[COLETA] usando cache local: {cache}")
        with cache.open(encoding="utf-8") as arquivo:
            return json.load(arquivo)

    print("[COLETA] cache ausente ou forçado — coletando da API (com retomada automática)")
    dados = coletar(SEEDS, cache_path=cache)

    print(f"[COLETA] {len(dados)} CNPJs salvos em {cache}")
    return dados

if __name__ == "__main__":

    carregar_ou_coletar(forcar=True)
