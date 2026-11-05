import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
payload = bytes.fromhex("033b1bd50cde58853fadffe08d1c0d3ac621e4da4e48ee131da5a72bd99d064af7af76f49095a693739f18714f41b6e15fe3eda04336309000")

iv = payload[:12]
ct = payload[12:-16]
tag = payload[-16:]

aesgcm = AESGCM(key)
try:
    pt = aesgcm.decrypt(iv, ct + tag, None)
    print("Decrypted:", pt)
except Exception as e:
    print("Decryption failed:", e)
