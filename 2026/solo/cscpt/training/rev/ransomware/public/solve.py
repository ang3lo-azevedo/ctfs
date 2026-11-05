#!/usr/bin/env python3
"""Solve script for the ransomware challenge.

Pipeline:
1) Parse locker.exe and recover the XOR key from DecodeAssembly::.cctor user string.
2) Recover the embedded payload from the field with RVA (5632 bytes) and decode it.
3) Parse decoded payload and recover:
   - KEY256 from Encryption::.cctor user string
   - IV bytes from the static field initialized via RuntimeHelpers.InitializeArray
4) Decrypt flag.txt.CSCPT.encrypted using AES-CBC + PKCS7.
"""

from pathlib import Path

import dnfile
from dncil.cil.body.reader import read_method_body_from_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


HERE = Path(__file__).resolve().parent
LOCKER = HERE / "locker.exe"
ENC_FILE = HERE / "flag.txt.CSCPT.encrypted"


def get_method_row(pe, type_name: str, method_name: str):
    for t in pe.net.mdtables.TypeDef:
        if str(t.TypeName) != type_name:
            continue
        for mi in t.MethodList:
            m = mi.row
            if str(m.Name) == method_name:
                return m
    raise ValueError(f"Method not found: {type_name}::{method_name}")


def iter_tokens_from_method(pe, method_row):
    off = pe.get_offset_from_rva(method_row.Rva)
    blob = pe.__data__[off : off + 1024]
    body = read_method_body_from_bytes(blob)
    for ins in body.instructions:
        text = str(ins)
        if "token(0x" in text:
            tok_hex = text.split("token(0x", 1)[1].split(")", 1)[0]
            yield int(tok_hex, 16)


def extract_loader_xor_key(locker_pe):
    cctor = get_method_row(locker_pe, "DecodeAssembly", ".cctor")
    for tok in iter_tokens_from_method(locker_pe, cctor):
        if (tok >> 24) == 0x70:
            off = tok & 0x00FFFFFF
            return locker_pe.net.user_strings.get(off).value.encode("utf-8")
    raise ValueError("Could not find DecodeAssembly key")


def extract_embedded_payload(locker_pe, xor_key: bytes):
    # Main loader allocates a 5632-byte array in RawAssembly::getAssembly.
    payload_len = 5632
    field_rva_row = list(locker_pe.net.mdtables.FieldRva)[0]
    data_off = locker_pe.get_offset_from_rva(field_rva_row.Rva)
    encoded = locker_pe.__data__[data_off : data_off + payload_len]
    return bytes(b ^ xor_key[i % len(xor_key)] for i, b in enumerate(encoded))


def extract_key256_and_iv(payload_pe):
    # KEY256 is loaded via ldstr in Encryption::.cctor
    enc_cctor = get_method_row(payload_pe, "Encryption", ".cctor")
    key256 = None
    for tok in iter_tokens_from_method(payload_pe, enc_cctor):
        if (tok >> 24) == 0x70:
            off = tok & 0x00FFFFFF
            key256 = payload_pe.net.user_strings.get(off).value.encode("utf-8")
            break
    if key256 is None:
        raise ValueError("Could not recover KEY256")

    # IV is in the only FieldRva row (16 static bytes initialized into an array).
    iv_row = list(payload_pe.net.mdtables.FieldRva)[0]
    iv_off = payload_pe.get_offset_from_rva(iv_row.Rva)
    iv = bytes(payload_pe.__data__[iv_off : iv_off + 16])

    return key256, iv


def decrypt_flag(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return unpad(cipher.decrypt(ciphertext), 16)


def main():
    locker_pe = dnfile.dnPE(str(LOCKER))
    xor_key = extract_loader_xor_key(locker_pe)

    payload = extract_embedded_payload(locker_pe, xor_key)
    payload_path = HERE / "decoded_payload.bin"
    payload_path.write_bytes(payload)

    payload_pe = dnfile.dnPE(str(payload_path))
    key, iv = extract_key256_and_iv(payload_pe)

    ciphertext = ENC_FILE.read_bytes()
    plaintext = decrypt_flag(ciphertext, key, iv)

    print("Recovered loader XOR key:", xor_key.decode("utf-8", errors="replace"))
    print("Recovered AES key:", key.decode("utf-8", errors="replace"))
    print("Recovered IV:", iv.hex())
    print("\nFlag:")
    print(plaintext.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
