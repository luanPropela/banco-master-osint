"""Baixa os CSVs de Carteira do DAIR por ANO via download por arquivo do Nextcloud (encoding %20 + path correto)."""
import os
from urllib.parse import quote
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TOKEN = "nX7bKdoXtagWTYo"
BASE = "https://serprodrive.serpro.gov.br"
OUT = "data/dair"
os.makedirs(OUT, exist_ok=True)

# o zip mostrou top "6 - DAIR/" -> a pasta compartilhada provavelmente é "6 - DAIR";
# então o path do arquivo, relativo à raiz do share, é "/Atualizado_ate_01_05_2026".
PATH_CANDS = ["/Atualizado_ate_01_05_2026", "/6 - DAIR/Atualizado_ate_01_05_2026", "/"]
ARQS = {
    "2023": "1.3 - Carteira_2023.csv",
    "2024": "1.4 - Carteira_2024.csv",
    "2025": "1.5 - Carteira_2025.csv",
    "2026": "1.6 - Carteira_2026.csv",
}


def baixar(ano, nome):
    dest = f"{OUT}/Carteira_{ano}.csv"
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        print(f"  já existe Carteira_{ano}.csv ({os.path.getsize(dest)/1e6:.1f} MB)"); return True
    for path in PATH_CANDS:
        url = f"{BASE}/s/{TOKEN}/download?path={quote(path)}&files={quote(nome)}"
        try:
            r = requests.get(url, headers=H, timeout=600, stream=True)
            ct = r.headers.get("content-type", "")
            if r.status_code != 200 or "html" in ct:
                continue
            total = 0
            with open(dest, "wb") as f:
                for ch in r.iter_content(1 << 20):
                    f.write(ch); total += len(ch)
            print(f"  Carteira_{ano}.csv -> {total/1e6:.1f} MB | {ct} | path={path!r}")
            return True
        except Exception as e:
            print(f"  Carteira_{ano} path={path!r} ERRO: {e}")
    print(f"  Carteira_{ano}: FALHOU em todos os paths")
    return False


def main():
    # testa 2024 primeiro
    if baixar("2024", ARQS["2024"]):
        for ano in ("2023", "2025", "2026"):
            baixar(ano, ARQS[ano])


if __name__ == "__main__":
    main()
