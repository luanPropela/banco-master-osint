"""Plano B p/ balanço do Master e BRB: CVM CIA_ABERTA (DFP/ITR). Checa presença + 1 tentativa www3 ifdata rest."""
import sys, io, re, requests, zipfile
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = {"User-Agent": "Mozilla/5.0", "Accept": "*/*"}


def main():
    print("=== www3 ifdata rest (a API do site, distinta do OData) ===")
    for u in ["https://www3.bcb.gov.br/ifdata/rest/anosMeses",
              "https://www3.bcb.gov.br/ifdata/rest/tiposInstituicao"]:
        try:
            r = requests.get(u, headers=H, timeout=40)
            print(f"  {r.status_code} {u.split('/rest/')[1]} -> {r.text[:120]}")
        except Exception as e:
            print(f"  ERRO {u}: {e}")

    print("\n=== CVM CIA_ABERTA — cadastro de emissores: Master e BRB presentes? ===")
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"
    r = requests.get(url, headers=H, timeout=120)
    df = pl.read_csv(io.BytesIO(r.content), separator=";", encoding="latin-1", infer_schema_length=0, ignore_errors=True)
    den = pl.col("DENOM_SOCIAL").cast(pl.String)
    hit = df.filter(den.str.contains(r"(?i)master|bras[ií]lia|\bbrb\b")).select([c for c in ["CNPJ_CIA","CD_CVM","DENOM_SOCIAL","SIT","SETOR_ATIV"] if c in df.columns])
    print(f"linhas: {df.height} | matches Master/BRB: {hit.height}")
    with pl.Config(tbl_rows=30, fmt_str_lengths=55, tbl_width_chars=170):
        print(hit)


if __name__ == "__main__":
    main()
