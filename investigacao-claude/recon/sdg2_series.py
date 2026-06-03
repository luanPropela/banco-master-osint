"""Série temporal do SDG II no Informe Mensal de FIDC + reconciliação com a matéria."""
import io, os, re, zipfile
import pandas as pd

CACHE = "data/cvm_fidc_mensal"
MESES = [f"2025{m:02d}" for m in range(1, 13)] + [f"2026{m:02d}" for m in range(1, 5)]
SDG2 = "46909301000133"


def norm(s):
    return re.sub(r"\D", "", str(s))


def tab(zf, t, ym):
    df = pd.read_csv(zf.open(f"inf_mensal_fidc_tab_{t}_{ym}.csv"),
                     sep=";", encoding="latin-1", dtype=str)
    df["c"] = df["CNPJ_FUNDO_CLASSE"].map(norm)
    return df


def num(df, col):
    if df.empty or col not in df.columns:
        return None
    v = pd.to_numeric(df[col].str.replace(",", "."), errors="coerce")
    return float(v.sum())


def main():
    print(f"{'comp':8} {'PL (R$)':>18} {'Ativo (R$)':>18} {'Dir.Cred (R$)':>18} {'cotistas':>9}")
    print("-" * 76)
    ult = None
    for ym in MESES:
        z = f"{CACHE}/inf_mensal_fidc_{ym}.zip"
        if not os.path.exists(z):
            continue
        zf = zipfile.ZipFile(z)
        try:
            i = tab(zf, "I", ym); i = i[i.c == SDG2]
        except KeyError:
            continue
        if i.empty:
            continue
        iv = tab(zf, "IV", ym); iv = iv[iv.c == SDG2]
        x1 = tab(zf, "X_1", ym); x1 = x1[x1.c == SDG2]

        pl = num(iv, "TAB_IV_A_VL_PL")
        ativo = num(i, "TAB_I_VL_ATIVO")
        # direitos creditórios: a vencer + vencidos (colunas TAB_I2A...)
        dircred_cols = [c for c in i.columns if c.startswith("TAB_I2A") or c == "TAB_I2A_VL_DIRCRED"]
        dircred = sum(filter(None, (num(i, c) for c in dircred_cols))) if dircred_cols else None
        cotst = int(pd.to_numeric(x1["TAB_X_NR_COTST"], errors="coerce").sum()) if not x1.empty else None

        def fmt(v):
            return f"{v:,.0f}" if v is not None else "—"
        print(f"{ym:8} {fmt(pl):>18} {fmt(ativo):>18} {fmt(dircred):>18} {str(cotst):>9}")
        ult = (ym, pl, ativo, dircred, cotst, i)

    if ult:
        ym, pl, ativo, dircred, cotst, i = ult
        print("\n=== DETALHE da última competência disponível:", ym, "===")
        row = i.iloc[0]
        for col in i.columns:
            val = row[col]
            if col in ("c",) or pd.isna(val) or str(val).strip() in ("", "0"):
                continue
            print(f"   {col:32} = {val}")


if __name__ == "__main__":
    main()
