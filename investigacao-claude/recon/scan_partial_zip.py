"""Varre os local file headers do zip PARCIAL para listar os nomes dos membros (sem zip completo)."""
import struct

F = "data/dair_serpro.zip"
SIG = b"PK\x03\x04"


def main():
    names = []
    with open(F, "rb") as fh:
        data = b""
        pos = 0
        CHUNK = 1 << 20
        carry = b""
        while True:
            buf = fh.read(CHUNK)
            if not buf:
                break
            blob = carry + buf
            i = 0
            while True:
                j = blob.find(SIG, i)
                if j < 0:
                    break
                if j + 30 <= len(blob):
                    try:
                        nlen = struct.unpack("<H", blob[j+26:j+28])[0]
                        if 1 <= nlen <= 300 and j + 30 + nlen <= len(blob):
                            name = blob[j+30:j+30+nlen].decode("utf-8", "replace")
                            if name and all(c.isprintable() or c in "/ -._" for c in name[:1]):
                                if name not in names:
                                    names.append(name)
                    except Exception:
                        pass
                i = j + 4
            carry = blob[-300:]  # overlap p/ assinatura cortada na borda

    print(f"=== {len(names)} membros encontrados no parcial ===")
    for n in names:
        print("  ", n)


if __name__ == "__main__":
    main()
