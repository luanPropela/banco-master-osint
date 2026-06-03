"""Gera um CSV tidy do Informe Mensal de FIDC para os fundos da teia Master.
Lê o cache em data/cvm_fidc_mensal/ (baixado por explore_fidc.py) e escreve
investigacao-claude/dados/fidc_mensal_fundos_master.csv — um registro por fundo/competência."""
import io, os, re, zipfile, csv
import pandas as pd

CACHE = "data/cvm_fidc_mensal"
OUT = "investigacao-claude/dados/fidc_mensal_fundos_master.csv"
MESES = [f"2025{m:02d}" for m in range(1, 13)] + [f"2026{m:02d}" for m in range(1, 5)]
ALVO = {
    "46909301000133": "SDG II FIDC-NP",
    "53273475000118": "Anna FICFIDC-NP",
    "29786909000107": "Lancia! FIDC",
    "34081900000122": "Gold Style FIDC-NP",
}
COLS_I = {
    "TAB_I_VL_ATIVO": "ativo", "TAB_I2_VL_CARTEIRA": "carteira",
    "TAB_I2A_VL_DIRCRED_RISCO": "dir_cred", "TAB_I2A3_VL_CRED_INAD": "dir_cred_inadimplente",
    "TAB_I2A11_VL_REDUCAO_RECUP": "provisao", "TAB_I2C_VL_VLMOB": "valores_mobiliarios",
    "TAB_I2C1_VL_DEBENTURE": "debentures", "TAB_I2H_VL_COTA_FIDC": "cotas_outros_fidc",
    "TAB_I4_VL_OUTRO_ATIVO": "outros_a_receber",
}


def norm(s):
    return re.sub(r"\D", "", str(s))


def n(df, col):
    if df.empty or col not in df.columns:
        return ""
    v = pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce").sum()
    return round(float(v), 2)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    rows = []
    for ym in MESES:
        z = f"{CACHE}/inf_mensal_fidc_{ym}.zip"
        if not os.path.exists(z):
            continue
        zf = zipfile.ZipFile(z)

        def tab(t):
            df = pd.read_csv(zf.open(f"inf_mensal_fidc_tab_{t}_{ym}.csv"), sep=";",
                             encoding="latin-1", dtype=str)
            df["c"] = df["CNPJ_FUNDO_CLASSE"].map(norm)
            return df

        dfI, dfIV, dfX = tab("I"), tab("IV"), tab("X_1")
        for cnpj, nome in ALVO.items():
            i = dfI[dfI.c == cnpj]
            if i.empty:
                continue
            iv = dfIV[dfIV.c == cnpj]
            x = dfX[dfX.c == cnpj]
            rec = {"competencia": f"{ym[:4]}-{ym[4:]}", "cnpj": cnpj, "fundo": nome,
                   "admin": (i.iloc[0].get("ADMIN") or "").strip(),
                   "pl": n(iv, "TAB_IV_A_VL_PL"),
                   "cotistas": int(pd.to_numeric(x["TAB_X_NR_COTST"], errors="coerce").sum()) if not x.empty else ""}
            for col, alias in COLS_I.items():
                rec[alias] = n(i, col)
            rows.append(rec)

    cols = ["competencia", "cnpj", "fundo", "admin", "pl", "cotistas"] + list(COLS_I.values())
    with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} linhas -> {OUT}")
    for cnpj, nome in ALVO.items():
        meses = [r["competencia"] for r in rows if r["cnpj"] == cnpj]
        print(f"  {nome:20} {len(meses)} competências [{meses[0] if meses else '-'}..{meses[-1] if meses else '-'}]")


if __name__ == "__main__":
    main()
