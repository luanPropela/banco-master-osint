SEEDS_MASTER: dict[str, str] = {
    "33923798000100": "Banco Master S.A.",
    "33884941000194": "Banco Master Múltiplo S.A.",
    "09526594000143": "Banco Master de Investimento S.A.",
    "58497702000102": "Banco Letsbank S.A.",
    "07875796000175": "Viking Participações Ltda",
    "23862762000100": "Will Financeira S.A. CFI",
    "51213651000109": "Will Bank Holding Financeira Ltda",
}

SEEDS_EXPANSAO: dict[str, str] = {
    "56823324000184": "STERN FIP Multiestratégia (entrou Viking 29/09/2025)",
    "33886862000112": "Master S/A Corretora CCTVM",
    "03566273000196": "Máxima Asset Management Ltda",
    "18223260000191": "Catálise Investimentos Ltda",
    "09121454000195": "Tercon Investimentos Ltda",
    "21180163000173": "MAM Asset Management",
    "18167777000100": "Acura Gestora de Recursos Ltda",
    "09463122000199": "Brava Gestora de Recursos",
    "16925467000182": "Global Gestão e Investimentos Ltda",
    "36040900000100": "Harbour Capital Administradora de Carteiras",
    "42373402000181": "Squalo Capital Gestora de Recursos Ltda",
    "03403181000195": "Infinity Asset Management",
    "06238550000120": "Monetiza Investimentos Ltda",
    "19207159000100": "Privatto Administração de Patrimônio Ltda",
    "21046086000163": "ID Gestora e Administradora de Recursos Ltda",
    "24515907000151": "Carmel Gestora de Ativos Ltda",
    "28264093000180": "Smart Agro Investimentos Ltda",
    "32764855000185": "Libertas Asset S/A",
    "47917164000141": "Bluemac Asset Management Ltda",
    "50543106000100": "Menestys Gestora de Recursos Ltda",
    "67030395000146": "Trustee DTVM",
    "61820817000109": "Banco Paulista S.A. (custodiante)",
}

SEEDS: dict[str, str] = {**SEEDS_MASTER, **SEEDS_EXPANSAO}

SEEDS_FIDC: dict[str, str] = {}

MAX_DEPTH: int = 2
DELAY_SEGUNDOS: float = 0.8
CACHE_PATH: str = "data/cnpjs.json"

COR_EMPRESA: str = "#4A90D9"
COR_PESSOA: str = "#E85D5D"
BG_GRAFO: str = "#1a1a2e"
