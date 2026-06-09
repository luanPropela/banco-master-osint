"""O CDB chega na carteira do SDG II (e dos outros FIDC da teia)? Lê o Informe Mensal (Tab I, VL_CDB)."""
import glob, re, zipfile
from collections import defaultdict
import pandas as pd

FIDS = {"46909301000133": "SDG II", "53273475000118": "Anna",
        "29786909000107": "Lancia!", "34081900000122": "Gold Style"}


def norm(s):
    return re.sub(r"\D", "", str(s))


def main():
    agg = defaultdict(float)
    meses = defaultdict(int)
    for z in sorted(glob.glob("data/cvm_fidc_mensal/*.zip")):
        ym = re.search(r"(\d{6})", z).group(1)
        try:
            df = pd.read_csv(zipfile.ZipFile(z).open(f"inf_mensal_fidc_tab_I_{ym}.csv"),
                             sep=";", encoding="latin-1", dtype=str)
        except Exception:
            continue
        df["c"] = df["CNPJ_FUNDO_CLASSE"].map(norm)
        for c, n in FIDS.items():
            s = df[df.c == c]
            if len(s):
                v = pd.to_numeric(str(s.iloc[0].get("TAB_I2E_VL_CDB", "0")).replace(",", "."), errors="coerce")
                agg[n] += (v or 0)
                meses[n] += 1
    print("CDB na carteira (Tab I, VL_CDB) — soma de todos os meses reportados:")
    for n in FIDS.values():
        print(f"  {n:11}: R$ {agg[n]:>16,.2f}   ({meses[n]} meses)")
    print("\n(VL_CDB = quanto o fundo tem em CDB como ATIVO. Zero = não segura CDB do Master.)")


if __name__ == "__main__":
    main()
