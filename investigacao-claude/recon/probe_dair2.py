"""Descobrir a estrutura do share DAIR (SERPRO/Nextcloud) sem baixar tudo."""
import re, requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
TOKEN = "nX7bKdoXtagWTYo"
BASE = "https://serprodrive.serpro.gov.br"


def sec(t): print("\n" + "=" * 66 + f"\n{t}\n" + "=" * 66)


def main():
    sec("(1) HTML do share — nomes embutidos")
    r = requests.get(f"{BASE}/s/{TOKEN}", headers=H, timeout=60)
    txt = r.text
    for pat in ["sharingToken", "filename", "dir\":", "subPath", "initialState"]:
        for m in re.findall(rf'["\']?{pat}["\']?\s*[:=]\s*["\']([^"\']+)', txt)[:3]:
            print(f"   {pat}: {m}")
    nomes = set(re.findall(r'[\w\-./ ]+\.(?:csv|xml|zip|xlsx|txt)', txt, re.I))
    print("   arquivos citados no HTML:", sorted(nomes)[:20] or "(nenhum)")

    sec("(2) PROPFIND no /public.php/dav/files/<token>/")
    try:
        r = requests.request("PROPFIND", f"{BASE}/public.php/dav/files/{TOKEN}/",
                             auth=(TOKEN, ""), headers={**H, "Depth": "1"}, timeout=60)
        print("   status", r.status_code)
        for m in re.findall(r"<d:href>([^<]+)</d:href>", r.text):
            print("   ", requests.utils.unquote(m))
    except Exception as e:
        print("   ERRO", e)

    sec("(3) primeiros 4MB do zip — nomes de membros (local file headers)")
    try:
        r = requests.get(f"{BASE}/s/{TOKEN}/download", headers={**H, "Range": "bytes=0-4000000"},
                         timeout=120, stream=True)
        buf = r.raw.read(4000000)
        print("   baixados", len(buf), "bytes | status", r.status_code)
        # PK\x03\x04 = local file header; nome vem no offset 30
        membros = []
        i = 0
        while True:
            j = buf.find(b"PK\x03\x04", i)
            if j < 0 or j + 30 > len(buf):
                break
            nlen = int.from_bytes(buf[j+26:j+28], "little")
            name = buf[j+30:j+30+nlen].decode("utf-8", "replace")
            if name:
                membros.append(name)
            i = j + 4
        for m in membros[:40]:
            print("   ", m)
        if not membros:
            print("   (nenhum header de membro nos primeiros 4MB — 1º arquivo é grande)")
    except Exception as e:
        print("   ERRO", e)


if __name__ == "__main__":
    main()
