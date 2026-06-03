"""Procura o 2º cotista do SDG II em Atas de Assembleia / Informe Trimestral do FNET.
Resiliente: retry, timeout curto, pula falhas, reusa arquivos já baixados."""
import os, re, time, glob
import requests
import pdfplumber

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
CNPJ = "46909301000133"
OUT = "data/fnet_docs"
os.makedirs(OUT, exist_ok=True)
PROCURA = re.compile(r"MKS|SOLU[ÇC][OÕ]ES|INTEGRADAS|ANNA|HANS|REAG MASTER|presen|cotist", re.I)


def listar():
    url = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
    p = {"d": 0, "s": 0, "l": 200, "o[0][dataEntrega]": "desc", "cnpjFundo": CNPJ}
    return requests.get(url, params=p, headers=H, timeout=60).json().get("data", [])


def baixar(doc_id):
    # reusa qualquer arquivo já salvo com esse id no nome
    for ex in glob.glob(f"{OUT}/*{doc_id}*.pdf"):
        return ex
    url = f"https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={doc_id}&cvm=true"
    for tent in range(3):
        try:
            r = requests.get(url, headers=H, timeout=60)
            if r.status_code == 200 and r.content[:4] == b"%PDF":
                path = f"{OUT}/doc_{doc_id}.pdf"
                open(path, "wb").write(r.content)
                return path
        except Exception:
            time.sleep(2 * (tent + 1))
    return None


def texto(path):
    try:
        with pdfplumber.open(path) as pdf:
            return "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    except Exception as e:
        return f"(erro: {e})"


def main():
    docs = listar()
    atas = [d for d in docs if "Assembleia" in str(d.get("categoriaDocumento"))]
    tri = [d for d in docs if "Trimestral" in str(d.get("tipoDocumento"))]
    alvo = atas + tri[:2]
    print(f"docs SDG II: {len(docs)} | atas de assembleia: {len(atas)} | trimestrais (2 + recentes): {len(tri)}")
    for d in alvo:
        did = d.get("id")
        cat = f"{d.get('categoriaDocumento')}/{d.get('tipoDocumento')}"
        path = baixar(did)
        if not path:
            print(f"  id={did} {d.get('dataEntrega')} {cat}: download falhou")
            continue
        t = texto(path)
        tem_mks = bool(re.search(r"MKS|SOLU[ÇC]", t, re.I))
        hits = [ln.strip() for ln in t.splitlines() if PROCURA.search(ln) and ln.strip()]
        print(f"\n  id={did} {d.get('dataEntrega')} {cat} | {'MKS PRESENTE!' if tem_mks else 'sem MKS'} | {len(hits)} linhas-alvo")
        for ln in hits[:10]:
            print(f"      {ln[:150]}")


if __name__ == "__main__":
    main()
