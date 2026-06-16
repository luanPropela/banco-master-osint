"""Balanço do BRB via CVM CIA_ABERTA (DFP anual + ITR trimestral). Ativo, PL, carteira de crédito ao longo do tempo."""
import sys, os, io, zipfile, requests
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
H = {"User-Agent": "Mozilla/5.0"}
BRB = "00000208000100"
CACHE = "data/cvm_cia"; os.makedirs(CACHE, exist_ok=True)
JOBS = [("ITR", y) for y in (2023, 2024, 2025, 2026)] + [("DFP", y) for y in (2023, 2024, 2025)]


def baixar(doc, y):
    f = f"{CACHE}/{doc.lower()}_{y}.zip"
    if not os.path.exists(f):
        url = f"https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/{doc}/DADOS/{doc.lower()}_cia_aberta_{y}.zip"
        r = requests.get(url, headers=H, timeout=180)
        if r.status_code != 200:
            return None
        open(f, "wb").write(r.content)
    return f


def ler(zf, nome):
    try:
        txt = zf.read(nome).decode("latin-1")  # CVM é ISO-8859-1; recodifica p/ utf-8
        return pl.read_csv(io.BytesIO(txt.encode("utf-8")), separator=";", infer_schema_length=0, ignore_errors=True)
    except Exception as e:
        print("  erro lendo", nome, e); return None


def main():
    rows = []
    for doc, y in JOBS:
        f = baixar(doc, y)
        if not f:
            continue
        zf = zipfile.ZipFile(f)
        for grp in ["BPA_con", "BPP_con", "BPA_ind", "BPP_ind"]:
            nome = f"{doc.lower()}_cia_aberta_{grp}_{y}.csv"
            if nome not in zf.namelist():
                continue
            df = ler(zf, nome)
            if df is None:
                continue
            df = df.filter((pl.col("CNPJ_CIA").cast(pl.String).str.replace_all(r"\D","") == BRB)
                           & (pl.col("ORDEM_EXERC") == "ÚLTIMO"))
            if df.height == 0:
                continue
            df = df.with_columns(pl.col("VL_CONTA").cast(pl.String).str.replace(",", ".").cast(pl.Float64, strict=False).alias("vl"),
                                 pl.lit(f"{doc}").alias("doc"), pl.lit("con" if "con" in grp else "ind").alias("base"))
            for r in df.iter_rows(named=True):
                ds = (r["DS_CONTA"] or "").upper(); cd = (r["CD_CONTA"] or "")
                key = None
                if cd == "1": key = "Ativo_Total"
                elif cd == "2.03": key = "PL"
                elif "RÉDIT" in ds or "CREDIT" in ds: key = f"Credito::{r['DS_CONTA']}"
                if key:
                    rows.append({"data": r["DT_FIM_EXERC"], "base": r["base"], "conta": key, "vl": r["vl"]})

    if not rows:
        print("nada encontrado p/ BRB"); return
    t = pl.DataFrame(rows).filter(pl.col("base") == "con")
    piv = (t.filter(pl.col("conta").is_in(["Ativo_Total", "PL"]))
             .pivot(values="vl", index="data", on="conta", aggregate_function="max").sort("data"))
    print("=== BRB — Ativo Total e PL (consolidado, R$) por data-base ===")
    with pl.Config(tbl_rows=40, tbl_width_chars=90): print(piv)
    print("\n=== contas de CRÉDITO do BRB (para ver o salto da carteira ~R$12bi) ===")
    cred = (t.filter(pl.col("conta").str.starts_with("Credito::"))
              .group_by(["data", "conta"]).agg(pl.col("vl").max().alias("vl")).sort(["conta", "data"]))
    with pl.Config(tbl_rows=60, fmt_str_lengths=55, tbl_width_chars=140): print(cred)
    pl.DataFrame(rows).write_csv("investigacao-claude/dados/brb_balanco_cvm.csv")
    print("\n-> investigacao-claude/dados/brb_balanco_cvm.csv")


if __name__ == "__main__":
    main()
