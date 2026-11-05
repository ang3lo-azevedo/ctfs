#!/usr/bin/env python3
from __future__ import annotations

import ctypes
import re
from pathlib import Path

from pypdf import PdfReader


HERE = Path(__file__).resolve().parent
OUTPUT_LOG = HERE / "output"
SEED_VALUE = 42
MASTER_KEY_SIZE = 64


def get_encryption_order() -> list[str]:
    order: list[str] = []
    for line in OUTPUT_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"Encrypting file (.+)$", line)
        if match:
            order.append(match.group(1))
    if not order:
        raise RuntimeError("Could not recover encryption order from output log")
    return order


def generate_master_key(seed_value: int) -> bytearray:
    libc = ctypes.CDLL(None)
    libc.srand(seed_value)
    return bytearray(libc.rand() & 0xFF for _ in range(MASTER_KEY_SIZE))


def update_key_for_filename(key: bytearray, filename: str) -> bytearray:
    filename_xor = 0
    for byte in filename.encode("utf-8"):
        filename_xor ^= byte
    return bytearray(byte ^ filename_xor for byte in key)


def decrypt_file(cipher_path: Path, key: bytearray) -> bytes:
    ciphertext = cipher_path.read_bytes()
    return bytes(byte ^ key[index % MASTER_KEY_SIZE] for index, byte in enumerate(ciphertext))


def update_key_with_plaintext_tail(key: bytearray, plaintext: bytes) -> bytearray:
    if len(plaintext) <= MASTER_KEY_SIZE - 1:
        return key
    tail = plaintext[-MASTER_KEY_SIZE:]
    return bytearray(left ^ right for left, right in zip(key, tail))


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts).strip()


def main() -> None:
    order = get_encryption_order()
    key = generate_master_key(SEED_VALUE)

    for name in order:
        key = update_key_for_filename(key, name)
        cipher_path = HERE / f"{name}.cipher"
        plaintext = decrypt_file(cipher_path, key)
        (HERE / name).write_bytes(plaintext)
        key = update_key_with_plaintext_tail(key, plaintext)

    print(extract_pdf_text(HERE / "lista_participantes.pdf"))


if __name__ == "__main__":
    main()