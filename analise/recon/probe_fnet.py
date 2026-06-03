"""Probe: o FNET (Fundos.NET / B3) tem API pública de documentos do SDG II?"""
import json
import requests

CNPJ = "46909301000133"
H = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,*/*"}

# endpoint público de pesquisa do FNET (lista de documentos)
URL = "https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados"
params = {
    "d": 0, "s": 0, "l": 30,
    "o[0][dataEntrega]": "desc",
    "cnpjFundo": CNPJ,
    "idCategoriaDocumento": 0,
    "idTipoDocumento": 0,
    "idEspecieDocumento": 0,
}
try:
    r = requests.get(URL, params=params, headers=H, timeout=60)
    print("status", r.status_code, "| ct", r.headers.get("content-type"))
    if r.status_code == 200 and "json" in (r.headers.get("content-type") or ""):
        j = r.json()
        total = j.get("recordsTotal")
        print("recordsTotal:", total)
        for d in j.get("data", [])[:30]:
            # campos típicos: denominacaoSocial, categoriaDocumento, tipoDocumento, dataEntrega, id
            print(f"  id={d.get('id')} | {d.get('dataEntrega')} | {d.get('categoriaDocumento')} / "
                  f"{d.get('tipoDocumento')} / {d.get('especieDocumento')} | {d.get('denominacaoSocial')}")
    else:
        print(r.text[:500])
except Exception as e:
    print("ERRO:", e)
