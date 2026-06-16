"""Espia o schema da Carteira DAIR e mostra linhas que mencionam Master/Reag (polars)."""
import polars as pl

F = "data/dair/Carteira_2026.csv"


def main():
    for sep in [";", ","]:
        try:
            lf = pl.scan_csv(F, separator=sep, encoding="utf8-lossy",
                             infer_schema_length=0, truncate_ragged_lines=True, ignore_errors=True)
            cols = lf.collect_schema().names()
            if len(cols) > 2:
                break
        except Exception:
            continue
    print(f"separador={sep!r} | {len(cols)} colunas")
    for c in cols:
        print("   -", c)

    df = lf.collect()
    print(f"\nlinhas: {df.height}")

    # procura MASTER/REAG/SDG/HANS em qualquer coluna textual
    pat = "(?i)MASTER|REAG|CBSF|HANS 95|\\bSDG\\b|\\bANNA\\b|LANCIA|GOLD STYLE|KATCH|UPPER"
    str_cols = [c for c, t in zip(df.columns, df.dtypes) if t == pl.String]
    mask = None
    for c in str_cols:
        m = df[c].str.contains(pat)
        mask = m if mask is None else (mask | m)
    hits = df.filter(mask.fill_null(False))
    print(f"\nlinhas mencionando Master/Reag/etc: {hits.height}")
    with pl.Config(tbl_cols=-1, fmt_str_lengths=40, tbl_width_chars=240):
        print(hits.head(6))


if __name__ == "__main__":
    main()
