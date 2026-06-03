"""
Reconstrução do SDG II a partir de fonte pública — confronto com a matéria Folha/ICL.

Itens extraídos e conferidos manualmente da Demonstração Financeira auditada do SDG II
(FNET id=963178, exercício 2024) e do Informe Mensal Estruturado de FIDC (dados abertos CVM).
Valores em R$ mil salvo indicação. Gera CSV em analise/recon/output/.
"""
import csv
import os

OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

# (data, cedente/origem, devedor/emissor, instrumento, valor_mil, doc)
CESSOES = [
    ("2024-02-27", "Banco Master S.A.",            "Lormont Participações S.A.", "CCB",        102_438, "DF id963178"),
    ("2024-12-19", "Banco Master S.A.",            "(não identificado)",         "Dir. Cred.", 192_941, "DF id963178"),
    ("2024-12-19", "Banco Master S.A.",            "(não identificado)",         "Dir. Cred.", 936_222, "DF id963178"),
    ("2024-09-27", "Carriet Inventory FIDC-NP",    "Lormont Participações S.A.", "CCB",        325_452, "DF id963178"),
    ("2024-12-31", "B-ROL FIDC-NP",                "Lormont Participações S.A.", "CCB",         41_417, "DF id963178"),
    ("2024-12-31", "CIB-K FIDC-NP",                "Lormont Participações S.A.", "CCB",         40_572, "DF id963178"),
    ("2024-12-31", "Del Rey FIDC-NP",              "Lormont Participações S.A.", "CCB",         43_107, "DF id963178"),
    ("2024-12-31", "Runeard FIDC-NP",              "Lormont Participações S.A.", "CCB",         43_953, "DF id963178"),
    ("2023-03-06", "Super Empreend. e Part. S.A.", "Super Empreend. e Part. S.A.","Dir. Cred.", 22_012, "DF id963178"),
    ("2023-11-22", "Banvox Holding Financeira S.A.","Banvox Holding Financeira S.A.","Debênture",380_346, "DF id963178"),
]

# (claim da matéria, valor citado R$, valor reconstruído R$ mil, fonte, status)
def main():
    # grava CSV das cessões
    with open(os.path.join(OUT, "sdg2_cessoes_reconstruidas.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["data", "cedente", "devedor_emissor", "instrumento", "valor_brl", "doc_fonte"])
        for d, ced, dev, instr, vmil, doc in CESSOES:
            w.writerow([d, ced, dev, instr, vmil * 1000, doc])

    master_direto = sum(v for _, c, _, _, v, _ in CESSOES if c == "Banco Master S.A.")
    master_dez19 = sum(v for d, c, _, _, v, _ in CESSOES if c == "Banco Master S.A." and d == "2024-12-19")
    lormont_total = sum(v for _, _, dev, _, v, _ in CESSOES if "Lormont" in dev)

    print("=" * 78)
    print("RECONCILIAÇÃO — matéria Folha/ICL  ×  dado público reconstruído")
    print("=" * 78)
    linhas = [
        ("Tamanho do fundo (ativo)",      "R$ 5,4 bi",   "R$ 5,455 bi (ativo, dez/2025)",            "Informe Mensal CVM", "EXATO"),
        ("Nº de cotistas",                "2",           "2 (jan/2025–jan/2026)",                    "Informe Mensal CVM", "EXATO"),
        ("Cotista = Anna (Hans via Anna)","—",           "Anna integraliza cotas 30/09/2024",        "DF id963178",        "CONFIRMADO"),
        ("Cotista = MKS Soluções",        "—",           "2o cotista classificado como FUNDO, MKS não nomeada", "Informe/DF", "NAO CONFIRMADO"),
        ("Créditos podres absorvidos",    "R$ 3,6 bi",   "Dir.cred. R$ 3,36 bi (dez/25) / R$ 6,53 bi (DF jan/24)", "Informe+DF", "COMPATIVEL"),
        ("Direto do Master",              ">= R$ 1,1 bi",f"R$ {master_dez19/1e6:.3f} bi (2 cessões 19/12/24); total Master R$ {master_direto/1e6:.3f} bi", "DF id963178", "EXATO"),
        ("Lormont (total no fundo)",      "~R$ 553 mi",  f"R$ {lormont_total/1000:.0f} mi (6 CCBs)", "DF id963178",        "COMPATIVEL"),
        ("Lormont cedido pelo Master",    "R$ 102 mi",   "R$ 102,438 mi (CCB, 27/02/2024)",          "DF id963178",        "EXATO"),
        ("Debênture Banvox",              "R$ 380 mi",   "R$ 380,346 mi adquirido (emissão R$ 400 mi)", "DF id963178",     "EXATO"),
        ("Super Empreendimentos",         "R$ 22 mi",    "R$ 22,012 mi (cessão 06/03/2023)",         "DF id963178",        "EXATO"),
        ("Indício de fraude (lastro)",    "implícito",   "ABSTENÇÃO de opinião; 62% dos dir.cred. sem lastro", "DF id963178 (parecer)", "CONFIRMADO"),
    ]
    print(f"{'Afirmação da matéria':32} {'Citado':12} {'Status':14} Reconstruído / fonte")
    print("-" * 78)
    rows = []
    for claim, cit, rec, fonte, status in linhas:
        print(f"{claim:32} {cit:12} {status:14} {rec}  [{fonte}]")
        rows.append([claim, cit, status, rec, fonte])
    with open(os.path.join(OUT, "sdg2_scorecard.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["afirmacao_materia", "valor_citado", "status", "valor_reconstruido", "fonte"])
        w.writerows(rows)

    print("\nResumo:", sum(1 for l in linhas if l[-1] in ("EXATO", "CONFIRMADO", "COMPATIVEL")),
          "de", len(linhas), "afirmações reproduzidas a partir de fonte pública;",
          "1 não confirmada (MKS como cotista).")
    print(f"CSVs gravados em {OUT}/")


if __name__ == "__main__":
    main()
