"""Probe da API OData do IF.data (BACEN) para achar o Banco Master e seu balanço trimestral."""
import sys, requests, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def get(url):
    r = requests.get(url, headers=H, timeout=90)
    return r.status_code, (r.json() if "json" in r.headers.get("content-type","") else r.text[:400])


def main():
    print("=== (1) service root — entity sets ===")
    sc, j = get(f"{ROOT}/?$format=json")
    print("status", sc)
    if isinstance(j, dict):
        for v in j.get("value", []):
            print("   -", v.get("name"), "|", v.get("url"))

    print("\n=== (2) IfDataCadastro (amostra) ===")
    sc, j = get(f"{ROOT}/IfDataCadastro?$format=json&$top=3")
    print("status", sc)
    if isinstance(j, dict) and j.get("value"):
        print("   colunas:", list(j["value"][0].keys()))
        print("   amostra:", json.dumps(j["value"][0], ensure_ascii=False)[:400])

    print("\n=== (3) procurar Banco Master no cadastro ===")
    for filt in ["contains(NomeInstituicao,'MASTER')", "contains(Instituicao,'MASTER')", "contains(NomeInstituicaoFinanceira,'MASTER')"]:
        sc, j = get(f"{ROOT}/IfDataCadastro?$format=json&$top=10&$filter={requests.utils.quote(filt)}")
        if isinstance(j, dict) and j.get("value"):
            print(f"   filtro {filt} -> {len(j['value'])} resultados")
            for v in j["value"][:8]:
                print("     ", json.dumps(v, ensure_ascii=False)[:200])
            break
        else:
            print(f"   filtro {filt} -> {sc} {str(j)[:120]}")


if __name__ == "__main__":
    main()
