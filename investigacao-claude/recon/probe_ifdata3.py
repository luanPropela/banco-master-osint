"""Lê o $metadata do IF.data OData p/ achar a assinatura exata das funções, e testa chamadas inline."""
import sys, re, requests, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata"
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def main():
    print("=== $metadata (assinaturas de função) ===")
    r = requests.get(f"{ROOT}/$metadata", headers=H, timeout=90)
    print("status", r.status_code, "| bytes", len(r.text))
    # extrai FunctionImport / Function com Parameters
    for blk in re.findall(r"<(?:Function|FunctionImport)\b[^>]*Name=\"(IfData\w+|ListaDeRelatorio)\"[\s\S]*?</(?:Function|FunctionImport)>", r.text)[:6]:
        pass
    for m in re.findall(r"<(Function|FunctionImport)([^>]*)>([\s\S]*?)</\1>", r.text):
        head, body = m[1], m[2]
        name = re.search(r'Name="([^"]+)"', head)
        if name and ("IfData" in name.group(1) or "Relatorio" in name.group(1)):
            params = re.findall(r'<Parameter Name="([^"]+)" Type="([^"]+)"', body)
            print(f"  {name.group(1)}({', '.join(f'{p}:{t}' for p,t in params)})")

    print("\n=== tentativas inline de IfDataCadastro ===")
    for url in [
        f"{ROOT}/IfDataCadastro(AnoMes=202412)?$top=5&$format=json",
        f"{ROOT}/IfDataCadastro(AnoMes=202412,TipoInstituicao=2)?$top=5&$format=json",
        f"{ROOT}/IfDataCadastro(AnoMes=202509)?$top=5&$format=json",
    ]:
        try:
            r = requests.get(url, headers=H, timeout=90)
            print(f"  {r.status_code}  {url.split('/odata/')[1][:70]}")
            if r.status_code == 200:
                v = r.json().get("value", [])
                if v:
                    print("     colunas:", list(v[0].keys()))
                break
        except Exception as e:
            print("   ERRO", e)


if __name__ == "__main__":
    main()
