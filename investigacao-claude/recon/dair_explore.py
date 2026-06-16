"""Explora o pacote DAIR: lista CSVs, acha o de carteira/fundos, extrai e mostra schema (polars)."""
import os, zipfile
import polars as pl

ZIP = "data/dair_serpro.zip"
EXTRACT_DIR = "data/dair"
os.makedirs(EXTRACT_DIR, exist_ok=True)


def main():
    zf = zipfile.ZipFile(ZIP)
    csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    print(f"=== {len(csvs)} CSVs no pacote ===")
    for n in sorted(csvs):
        print(f"  {zf.getinfo(n).file_size/1e6:8.1f} MB  {n}")

    # candidatos a "carteira / fundos analisados / portfólio"
    alvos = [n for n in csvs if any(k in n.lower() for k in
             ["carteira", "fundo de investimento", "portf", "ativo"])]
    print(f"\n=== candidatos (carteira/fundos): {alvos} ===")

    for n in alvos:
        dest = os.path.join(EXTRACT_DIR, os.path.basename(n))
        if not os.path.exists(dest):
            with zf.open(n) as src, open(dest, "wb") as out:
                out.write(src.read())
        # schema + amostra via scan_csv lazy
        try:
            lf = pl.scan_csv(dest, separator=";", encoding="utf8-lossy",
                             infer_schema_length=0, truncate_ragged_lines=True)
            cols = lf.collect_schema().names()
            n_rows = lf.select(pl.len()).collect().item()
            print(f"\n--- {os.path.basename(n)} | {n_rows} linhas | {len(cols)} colunas")
            print("    colunas:", cols)
            print(lf.head(3).collect())
        except Exception as e:
            print(f"   erro lendo {n}: {e}")


if __name__ == "__main__":
    main()
