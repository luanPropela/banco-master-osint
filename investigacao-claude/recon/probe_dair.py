"""Sondar acesso programático ao DAIR (carteira dos RPPS) da Secretaria de Previdência.
Testa: compartilhamento Nextcloud do SERPRO + dados.gov.br."""
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TOKEN = "nX7bKdoXtagWTYo"
BASE = "https://serprodrive.serpro.gov.br"


def sec(t): print("\n" + "=" * 68 + f"\n{t}\n" + "=" * 68)


def main():
    sec("(1) share Nextcloud do SERPRO acessível?")
    for url in [f"{BASE}/s/{TOKEN}", f"{BASE}/s/{TOKEN}/download"]:
        try:
            r = requests.get(url, headers=H, timeout=60, stream=True)
            print(f"  GET {url}\n     -> {r.status_code} | {r.headers.get('content-type')} | len={r.headers.get('content-length')}")
        except Exception as e:
            print(f"  GET {url} -> ERRO {e}")

    sec("(2) WebDAV público (PROPFIND) — listar arquivos do share")
    try:
        r = requests.request("PROPFIND", f"{BASE}/public.php/webdav/", auth=(TOKEN, ""),
                             headers={**H, "Depth": "1"}, timeout=60)
        print("  status", r.status_code, "| bytes", len(r.content))
        import re
        for m in re.findall(r"<d:href>([^<]+)</d:href>", r.text)[:40]:
            print("   ", m)
    except Exception as e:
        print("  ERRO", e)

    sec("(3) dados.gov.br — busca por DAIR / investimentos RPPS")
    for q in ["dair", "investimentos+rpps", "regime+proprio+previdencia"]:
        try:
            u = f"https://dados.gov.br/api/publico/conjuntos-dados?isPrivado=false&nomeConjuntoDados={q}"
            r = requests.get(u, headers={**H, "Accept": "application/json"}, timeout=60)
            print(f"  q={q!r} -> {r.status_code} | {r.text[:200]}")
        except Exception as e:
            print(f"  q={q!r} -> ERRO {e}")


if __name__ == "__main__":
    main()
