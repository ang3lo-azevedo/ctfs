import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
payload = bytes.fromhex("6330d8f2c99b90daf7db3ced1f16e4c11a3d8b2677f87f04cbff55aa4b3713d6f94f940bf844daa2c21296562896fc64fdac4d13991eaaea487cb16ea3b4afb45f4819ec683c5f283554731ed67d2fc204c77a552e6909589e0dce43ee1539c917a3099c1b843205e3167a6bca81218484f7169a3e5a34c62130ce44be725c19c5b6061d6f")

iv = payload[:12]
ct = payload[12:-16]
tag = payload[-16:]

aesgcm = AESGCM(key)
try:
    pt = aesgcm.decrypt(iv, ct + tag, None)
    print("Decrypted:", pt)
except Exception as e:
    print("Decryption failed:", e)
