"""Fecha gaps: (1) RioPrev = 'Governo do Estado do RJ' no DAIR? carteira completa + fundos.
(2) varre TODOS os 'Governo do Estado de X' por exposicao Master. (3) re-tenta IF.data p/ BRB."""
import sys, glob, requests
import polars as pl
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ARQS = sorted(glob.glob("data/dair/Carteira_20*.csv"))
NOME = "Nome do Fundo / Banco da Conta"
MASTER_RE = r"(?i)master|reag|cbsf|hans 95|sdg ?ii|lancia|gold style|katch|anna fundo"
GEN = r"(?i)safra|\bbb \b|banrisul|brasil capital|tenax|santos credit|multisetorial"  # 'master' generico


def num(c): return (pl.col(c).cast(pl.String).str.replace_all(r"\.","").str.replace(",",".").cast(pl.Float64, strict=False))
def ckx(): c=pl.col("Competência").cast(pl.String).str.zfill(6); return c.str.slice(2,4)+c.str.slice(0,2)


def main():
    lf = pl.concat([pl.scan_csv(a, separator=";", encoding="utf8-lossy", infer_schema_length=0,
                                truncate_ragged_lines=True, ignore_errors=True) for a in ARQS], how="vertical_relaxed").collect()
    lf = lf.with_columns(num("Valor Total Atual").alias("v"), ckx().alias("ck"))
    nome = pl.col(NOME).cast(pl.String)

    # (1) RJ estado — carteira total vs Master, e os fundos que segura
    rj = lf.filter(pl.col("Ente").cast(pl.String).str.contains(r"(?i)governo do estado do rio de janeiro"))
    print("=== (1) Governo do Estado do RJ — CNPJ(s):", rj["CNPJ"].unique().to_list())
    tot = rj.group_by("ck").agg(pl.col("v").sum().alias("carteira_total")).sort("ck")
    mas = rj.filter(nome.str.contains(MASTER_RE) & ~nome.str.contains(GEN)).group_by("ck").agg(pl.col("v").sum().alias("master")).sort("ck")
    j = tot.join(mas, on="ck", how="left").with_columns((pl.col("master")/pl.col("carteira_total")*100).round(1).alias("pct_master"))
    print("carteira total vs Master (R$, por competência):")
    with pl.Config(tbl_rows=40, tbl_width_chars=90): print(j)
    print("\nMaiores ativos Master/Reag do RJ (nome | pico R$):")
    big = (rj.filter(nome.str.contains(MASTER_RE) & ~nome.str.contains(GEN)).group_by(NOME).agg(pl.col("v").max().alias("pico")).sort("pico", descending=True))
    with pl.Config(tbl_rows=15, fmt_str_lengths=55, tbl_width_chars=140): print(big.head(15))

    # (2) todos os 'Governo do Estado' com Master
    est = lf.filter(pl.col("Ente").cast(pl.String).str.contains(r"(?i)governo do estado"))
    estm = est.filter(nome.str.contains(MASTER_RE) & ~nome.str.contains(GEN)).group_by(["Ente","UF"]).agg(pl.col("v").max().alias("pico_master")).sort("pico_master", descending=True)
    print("\n=== (2) Governos ESTADUAIS com exposição Master (não-genérica) ===")
    with pl.Config(tbl_rows=20, fmt_str_lengths=38, tbl_width_chars=120): print(estm)

    # (3) IF.data retry p/ BRB
    print("\n=== (3) IF.data retry ===")
    for url in ["https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/IfDataCadastro?$format=json&$top=3",
                "https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/odata/ListaDeRelatorio?$format=json&$top=3"]:
        try:
            r = requests.get(url, headers={"User-Agent":"Mozilla/5.0","Accept":"application/json"}, timeout=60)
            print(f"  {r.status_code} {url.split('odata/')[1][:40]} -> {str(r.text)[:120]}")
        except Exception as e:
            print("  ERRO", e)


if __name__ == "__main__":
    main()
