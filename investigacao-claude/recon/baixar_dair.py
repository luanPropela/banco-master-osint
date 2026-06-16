"""Baixa o pacote DAIR (SERPRO) com guarda de tamanho e lista os CSVs."""
import os, zipfile, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
URL = "https://serprodrive.serpro.gov.br/s/nX7bKdoXtagWTYo/download"
OUT = "data/dair_serpro.zip"
CAP = 2_000_000_000  # 2 GB

os.makedirs("data", exist_ok=True)


def main():
    if os.path.exists(OUT) and os.path.getsize(OUT) > 1_000_000:
        print(f"já existe {OUT} ({os.path.getsize(OUT)/1e6:.1f} MB)")
    else:
        print("baixando", URL)
        r = requests.get(URL, headers=H, timeout=600, stream=True)
        total = 0
        with open(OUT, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk); total += len(chunk)
                if total % (50 << 20) < (1 << 20):
                    print(f"   {total/1e6:.0f} MB...")
                if total > CAP:
                    print("   CAP atingido, abortando"); break
        print(f"baixado: {total/1e6:.1f} MB -> {OUT}")

    print("\n=== membros do zip ===")
    zf = zipfile.ZipFile(OUT)
    infos = zf.infolist()
    print(f"total de membros: {len(infos)}")
    for i in infos:
        if i.filename.lower().endswith((".csv", ".xml", ".xlsx")):
            print(f"   {i.file_size/1e6:8.1f} MB  {i.filename}")


if __name__ == "__main__":
    main()
