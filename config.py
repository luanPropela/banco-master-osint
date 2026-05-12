"""
Configurações centralizadas do projeto.

Este módulo concentra todas as constantes (seeds, parâmetros de coleta e
cores da visualização). Centralizar evita números mágicos espalhados pelo
código e facilita ajustes sem precisar caçar valores em múltiplos arquivos.
"""

# ---------------------------------------------------------------------------
# Sementes do conglomerado Master.
# Chave = CNPJ (apenas dígitos, 14 caracteres). Valor = razão social descritiva.
# O BFS de `coleta.py` parte daqui e expande seguindo os sócios pessoa-jurídica.
# ---------------------------------------------------------------------------
SEEDS: dict[str, str] = {
    "33923798000100": "Banco Master S.A.",
    "33884941000194": "Banco Master Múltiplo S.A.",
    "09526594000143": "Banco Master de Investimento S.A.",
    "58497702000102": "Banco Letsbank S.A.",
    "07875796000175": "Viking Participações Ltda",
    "23862762000100": "Will Financeira S.A. CFI",
    "51213651000109": "Will Bank Holding Financeira Ltda",
}

# ---------------------------------------------------------------------------
# Parâmetros de coleta.
# ---------------------------------------------------------------------------
MAX_DEPTH: int = 2              # profundidade máxima do BFS
DELAY_SEGUNDOS: float = 0.8     # pausa entre requisições (API pública gratuita)
CACHE_PATH: str = "data/cnpjs.json"

# ---------------------------------------------------------------------------
# Parâmetros de visualização.
# ---------------------------------------------------------------------------
COR_EMPRESA: str = "#4A90D9"    # azul para nós empresa (PJ)
COR_PESSOA: str = "#E85D5D"     # vermelho para nós pessoa (PF)
BG_GRAFO: str = "#1a1a2e"       # fundo escuro do grafo PyVis
