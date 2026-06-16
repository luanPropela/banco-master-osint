"""Probe v2 do IF.data OData (recursos parametrizados por AnoMes). Acha o Banco Master e os relatórios."""
import sys, requests, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def get(url):
    r = requests.get(url, headers=H, timeout=120)
    ct = r.headers.get("content-type", "")
    return r.status_code, (r.json() if "json" in ct else r.text[:300])


def main():
    for anomes in ["202412", "202506", "202509"]:
        print(f"\n=== IfDataCadastro(AnoMes={anomes}) ===")
        sc, j = get(f"{ROOT}/IfDataCadastro(AnoMes=@AnoMes)?@AnoMes={anomes}&$format=json&$top=20000")
        print("status", sc)
        if isinstance(j, dict) and j.get("value"):
            rows = j["value"]
            print("   colunas:", list(rows[0].keys()))
            masters = [r for r in rows if "MASTER" in str(r).upper()]
            print(f"   instituições no período: {len(rows)} | com MASTER: {len(masters)}")
            for r in masters[:10]:
                print("     ", json.dumps(r, ensure_ascii=False)[:240])
            if masters:
                break
        else:
            print("   ", str(j)[:200])

    print(f"\n=== ListaDeRelatorio(AnoMes=202412) ===")
    sc, j = get(f"{ROOT}/ListaDeRelatorio(AnoMes=@AnoMes)?@AnoMes=202412&$format=json")
    print("status", sc)
    if isinstance(j, dict) and j.get("value"):
        for r in j["value"][:30]:
            print("   ", json.dumps(r, ensure_ascii=False)[:200])


if __name__ == "__main__":
    main()
