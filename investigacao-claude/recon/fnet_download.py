"""Baixa documentos do FNET por id. Testa exibir/download e detecta tipo real."""
import base64, os, sys
import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
OUT = "data/fnet_docs"
os.makedirs(OUT, exist_ok=True)

# ids de interesse do SDG II (DFs + informe trimestral mais recente)
DOCS = {
    "963178": "SDG2_DemonstracoesFinanceiras_A",
    "963141": "SDG2_DemonstracoesFinanceiras_B",
    "963349": "SDG2_DF_FusaoCisaoIncorp",
    "1199328": "SDG2_InformeTrimestral_2026-05-19",
}


def try_download(doc_id):
    for ep in ("downloadDocumento", "exibirDocumento"):
        url = f"https://fnet.bmfbovespa.com.br/fnet/publico/{ep}?id={doc_id}&cvm=true"
        try:
            r = requests.get(url, headers=H, timeout=120)
        except Exception as e:
            print(f"   {ep}: ERRO {e}"); continue
        ct = r.headers.get("content-type", "")
        print(f"   {ep}: {r.status_code} | {ct} | {len(r.content)} bytes")
        if r.status_code != 200 or not r.content:
            continue
        data = r.content
        # FNET às vezes devolve base64 do PDF como texto
        if b"%PDF" not in data[:1024]:
            try:
                dec = base64.b64decode(data, validate=False)
                if dec[:4] == b"%PDF":
                    data = dec
            except Exception:
                pass
        ext = "pdf" if data[:4] == b"%PDF" else ("html" if b"<html" in data[:2048].lower() else "bin")
        return data, ext
    return None, None


def main():
    for doc_id, name in DOCS.items():
        print(f"== id={doc_id} ({name}) ==")
        data, ext = try_download(doc_id)
        if data:
            path = f"{OUT}/{name}_{doc_id}.{ext}"
            open(path, "wb").write(data)
            print(f"   -> salvo {path} ({len(data)} bytes, tipo={ext})")
        print()


if __name__ == "__main__":
    main()
