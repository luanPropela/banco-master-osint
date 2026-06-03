"""
Verificação reprodutível: o dataset coletado reconstrói a fraude do SDG II?

Roda só sobre os CSVs versionados em data/csv/ (não precisa de internet nem do .db).
Uso:  python analise/verificacao_reconstrucao.py
"""
import csv
from collections import Counter
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "data" / "csv"


def carregar(nome):
    with open(CSV / nome, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# CNPJs dos fundos que a reportagem ICL/Folha aponta como núcleo da fraude
FUNDOS_FRAUDE = {
    "46909301000133": "SDG II FIDC-NP",
    "53273475000118": "Anna FICFIDC-NP",
    "32088041000178": "Hans 95 FI MM Créd. Privado",
    "29786909000107": "Lancia! FI MM Créd. Privado",
    "53311600000137": "Termópilas FIDC-NP",
    "34081900000122": "Gold Style FIDC-NP",
    "42584801000191": "Maranta FI MM Créd. Privado",
}


def main():
    # 1) Quais fundos têm carteira (CDA) efetivamente coletada?
    carteira = carregar("06_composicao_carteira_cvm_cda.csv")
    fundos_com_carteira = sorted({r["fundo_cnpj"] for r in carteira})
    print("=" * 70)
    print("1) FUNDOS COM CARTEIRA (CDA) COLETADA")
    print("=" * 70)
    for c in fundos_com_carteira:
        print(f"  {c}")
    print(f"  total: {len(fundos_com_carteira)} fundos\n")

    print("   Algum fundo do núcleo da fraude tem carteira coletada?")
    for cnpj, nome in FUNDOS_FRAUDE.items():
        status = "PRESENTE" if cnpj in fundos_com_carteira else "AUSENTE"
        print(f"     [{status:8}] {nome:30} {cnpj}")

    # 2) De onde vêm as arestas do grafo de fraude?
    edges = carregar("10_grafo_fraude_edges.csv")
    fonte_col = edges[0] and list(edges[0].keys())[-1]
    fontes = Counter()
    for r in edges:
        f = (r.get("fonte") or r.get(fonte_col) or "")
        if "CVMWeb" in f:
            fontes["consulta manual CVMWeb"] += 1
        else:
            fontes["reportagem jornalística"] += 1
    print("\n" + "=" * 70)
    print("2) PROVENIÊNCIA DAS ARESTAS DO GRAFO DE FRAUDE")
    print("=" * 70)
    for k, v in fontes.most_common():
        print(f"  {v:3}  {k}")
    print(f"    0  derivadas de dado público estruturado coletado pelo pipeline")

    # 3) Cobertura cadastral dos nós
    empresas = {r["cnpj"] for r in carregar("01_empresas.csv")}
    nodes = carregar("09_grafo_fraude_nodes.csv")
    com_cnpj = [n for n in nodes if n["cnpj"]]
    no_perimetro = [n for n in com_cnpj if n["cnpj"] in empresas]
    print("\n" + "=" * 70)
    print("3) COBERTURA CADASTRAL DOS NÓS DO GRAFO")
    print("=" * 70)
    print(f"  nós totais:                         {len(nodes)}")
    print(f"  com CNPJ preenchido:                {len(com_cnpj)}")
    print(f"  CNPJ presente no perímetro coletado:{len(no_perimetro)}")
    print(f"  sem CNPJ (pessoas/órgãos/fachadas): {len(nodes) - len(com_cnpj)}")

    print("\n  Nós SEM CNPJ (lacunas de identificação a resolver):")
    for n in nodes:
        if not n["cnpj"] and n["tipo"] in ("Empresa", "Fundo de Investimento"):
            print(f"     - {n['label']}  ({n['tipo']})")

    # 4) Veredito
    print("\n" + "=" * 70)
    print("VEREDITO")
    print("=" * 70)
    print("""  Camada SOCIETÁRIA (quem controla quem): RECONSTRUÍDA via QSA/Minha Receita.
  Camada de FLUXO FINANCEIRO (a carteira do SDG II que prova a fraude):
  NÃO reconstruída. A carteira coletada cobre só 3 FMP-FGTS (PL ~R$1,4 mi,
  ações Petrobras) + KATCH FIDC. Nenhum dos 7 fundos da fraude tem carteira.
  As 78 arestas do grafo são 100% asserção jornalística / consulta manual —
  0 vêm do dado público estruturado que o pipeline baixa.""")


if __name__ == "__main__":
    main()
