"""Tipo dos cotistas do SDG II (Tab X_1_1) + snapshot dez/2025 (mês do 'R$5,4 bi')."""
import io, os, re, zipfile
import pandas as pd

CACHE = "data/cvm_fidc_mensal"
SDG2 = "46909301000133"


def norm(s):
    return re.sub(r"\D", "", str(s))


def tab(ym, t):
    zf = zipfile.ZipFile(f"{CACHE}/inf_mensal_fidc_{ym}.zip")
    df = pd.read_csv(zf.open(f"inf_mensal_fidc_tab_{t}_{ym}.csv"),
                     sep=";", encoding="latin-1", dtype=str)
    df["c"] = df["CNPJ_FUNDO_CLASSE"].map(norm)
    return df[df.c == SDG2]


def main():
    # Tipo de cotistas (Tab X_1_1) — última competência com 2 cotistas (jan/2026)
    for ym in ("202601", "202512", "202603"):
        d = tab(ym, "X_1_1")
        if d.empty:
            continue
        print(f"=== SDG II — composição de cotistas por tipo (Tab X_1_1) {ym} ===")
        row = d.iloc[0]
        for col in d.columns:
            if col in ("c", "TP_FUNDO_CLASSE", "CNPJ_FUNDO_CLASSE", "DENOM_SOCIAL", "DT_COMPTC"):
                continue
            v = pd.to_numeric(pd.Series([row[col]]).str.replace(",", "."), errors="coerce").iloc[0]
            if v and v > 0:
                print(f"   {col:42} = {int(v)}")
        print()

    print("=== SDG II — snapshot dez/2025 (ativo ~R$5,4 bi citado na matéria) ===")
    i = tab("202512", "I").iloc[0]
    campos = {
        "TAB_I_VL_ATIVO": "Ativo total",
        "TAB_I2_VL_CARTEIRA": "Carteira",
        "TAB_I2A_VL_DIRCRED_RISCO": "Direitos creditórios (com risco)",
        "TAB_I2A3_VL_CRED_INAD": "  dos quais inadimplentes",
        "TAB_I2A11_VL_REDUCAO_RECUP": "  provisão p/ redução/recuperação",
        "TAB_I2C_VL_VLMOB": "Valores mobiliários",
        "TAB_I2C1_VL_DEBENTURE": "  debêntures",
        "TAB_I2H_VL_COTA_FIDC": "Cotas de outros FIDC",
        "TAB_I4_VL_OUTRO_ATIVO": "Outros ativos a receber",
    }
    for col, lbl in campos.items():
        if col in i.index and str(i[col]).strip() not in ("", "nan"):
            v = float(str(i[col]).replace(",", "."))
            print(f"   {lbl:38} R$ {v:>18,.2f}")


if __name__ == "__main__":
    main()
