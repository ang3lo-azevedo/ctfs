import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

key = bytes.fromhex("2b7e151628aed2a6abf7158809cf4f3c")
aesgcm = AESGCM(key)

with open("payload.hex", "r") as f:
    lines = f.readlines()

decrypted_data = b""
for line in lines:
    line = line.strip()
    if not line:
        continue
    try:
        payload = bytes.fromhex(line)
        iv = payload[:12]
        ct = payload[12:-16]
        tag = payload[-16:]
        pt = aesgcm.decrypt(iv, ct + tag, None)
        decrypted_data += pt
    except Exception as e:
        pass

with open("decrypted_stealer_data.txt", "wb") as f:
    f.write(decrypted_data)
print("Decrypted data written to decrypted_stealer_data.txt")
