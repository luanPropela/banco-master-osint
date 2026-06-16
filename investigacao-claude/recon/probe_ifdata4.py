"""IF.data voltou? Descobre a sintaxe (metadata/swagger) e tenta achar Banco Master e BRB."""
import sys, re, json, requests
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1"
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def g(url, to=60):
    try:
        r = requests.get(url, headers=H, timeout=to); return r.status_code, r
    except Exception as e:
        return None, str(e)


def main():
    print("=== root ==="); sc, r = g(f"{ROOT}/odata/?$format=json"); print(sc)
    print("\n=== $metadata (assinaturas) ==="); sc, r = g(f"{ROOT}/odata/$metadata")
    print("status", sc)
    if sc == 200:
        for m in re.findall(r"<(Function|FunctionImport)[^>]*Name=\"([^\"]+)\"[\s\S]*?</\1>", r.text):
            nm = m[1]
            if "IfData" in nm or "Relatorio" in nm:
                params = re.findall(r'<Parameter Name="([^"]+)" Type="([^"]+)"', m[0] if False else r.text[r.text.find(nm):r.text.find(nm)+400])
                print(f"  {nm}: {params[:6]}")

    print("\n=== tentativas IfDataCadastro (varias competencias e sintaxes) ===")
    ok = None
    for am in ["202509","202506","202503","202412","202406","202312"]:
        for url in [f"{ROOT}/odata/IfDataCadastro(AnoMes={am})?$format=json&$top=20000",
                    f"{ROOT}/odata/IfDataCadastro(AnoMes=@AnoMes)?@AnoMes={am}&$format=json&$top=20000"]:
            sc, r = g(url, 120)
            tag = url.split('odata/')[1][:34]
            if sc == 200 and isinstance(r, requests.Response):
                try:
                    v = r.json().get("value", [])
                except Exception:
                    v = []
                print(f"  200 {am} {tag} -> {len(v)} linhas")
                if v:
                    ok = (am, v); break
            else:
                txt = (r.text[:90] if isinstance(r, requests.Response) else str(r))
                print(f"  {sc} {am} {tag} -> {txt}")
        if ok: break

    if ok:
        am, v = ok
        cols = list(v[0].keys()); print("\n  colunas:", cols)
        alvo = [x for x in v if re.search(r"MASTER|BRB|BANCO DE BRASILIA|BRASÍLIA", json.dumps(x, ensure_ascii=False), re.I)]
        print(f"  registros MASTER/BRB em {am}: {len(alvo)}")
        for x in alvo[:12]:
            print("   ", json.dumps(x, ensure_ascii=False)[:200])


if __name__ == "__main__":
    main()
