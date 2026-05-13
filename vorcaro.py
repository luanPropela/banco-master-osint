import json
import webbrowser
from pathlib import Path

from pyvis.network import Network

ALVO = "VORCARO"
CACHE = Path("data/cnpjs.json")
SAIDA = "vorcaro.html"
BG = "#1a1a2e"

def carregar_cache() -> dict:
    if not CACHE.exists():
        raise FileNotFoundError(f"Cache não encontrado: {CACHE}. Rode `python main.py` primeiro.")
    with CACHE.open(encoding="utf-8") as arquivo:
        return json.load(arquivo)

def encontrar_empresas_do_alvo(dados: dict, termo: str) -> list[tuple[str, dict, dict]]:
    encontradas = []
    for cnpj, info in dados.items():
        for socio in info.get("qsa", []):
            nome = (socio.get("nome_socio") or "").upper()
            if termo.upper() in nome:
                encontradas.append((cnpj, info, socio))
                break
    return encontradas

def montar_html(dados: dict, empresas_alvo: list, saida: str) -> None:
    net = Network(height="100vh", width="100%", bgcolor=BG,
                  font_color="white", directed=True,
                  cdn_resources="remote", notebook=False)
    net.barnes_hut(gravity=-8000, spring_length=180)

    nome_alvo = empresas_alvo[0][2].get("nome_socio", ALVO)
    net.add_node(nome_alvo, label=nome_alvo,
                 color="#FFD700", size=40, shape="star",
                 title=f"<b>{nome_alvo}</b><br>aparece em {len(empresas_alvo)} empresa(s) Master")

    for cnpj, info, socio_alvo in empresas_alvo:
        razao = info.get("razao_social", cnpj)
        situacao = info.get("descricao_situacao_cadastral", "")
        net.add_node(cnpj,
                     label=razao[:35],
                     color="#4A90D9", size=25, shape="dot",
                     title=f"<b>{razao}</b><br>situação: {situacao}<br>UF: {info.get('uf','')}")
        net.add_edge(nome_alvo, cnpj,
                     label=socio_alvo.get("qualificacao_socio", ""),
                     color="#FFD700", arrows="to")

        for outro in info.get("qsa", []):
            nome_outro = outro.get("nome_socio")
            if not nome_outro or nome_outro == nome_alvo:
                continue
            net.add_node(nome_outro, label=nome_outro[:30],
                         color="#E85D5D", size=15, shape="dot",
                         title=f"<b>{nome_outro}</b><br>{outro.get('qualificacao_socio','')}")
            net.add_edge(nome_outro, cnpj,
                         label=outro.get("qualificacao_socio", ""),
                         color="#888", arrows="to")

    html = net.generate_html().replace(
        "<body>", f"<body style='margin:0;padding:0;background:{BG};'>")
    Path(saida).write_text(html, encoding="utf-8")
    webbrowser.open(f"file:///{Path(saida).resolve()}")
    print(f"[VORCARO] HTML salvo: {Path(saida).resolve()}")

def main() -> None:
    dados = carregar_cache()
    empresas = encontrar_empresas_do_alvo(dados, ALVO)
    if not empresas:
        print(f"[VORCARO] '{ALVO}' não encontrado no QSA das empresas coletadas.")
        return

    print(f"[VORCARO] {ALVO} aparece em {len(empresas)} empresa(s):")
    for cnpj, info, socio in empresas:
        print(f"  • {info['razao_social'][:55]:55} — {socio['qualificacao_socio']}")

    montar_html(dados, empresas, SAIDA)

if __name__ == "__main__":
    main()
