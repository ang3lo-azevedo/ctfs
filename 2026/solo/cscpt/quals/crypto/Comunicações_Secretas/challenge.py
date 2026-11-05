from Crypto.Cipher import AES
from Crypto.Util import Counter
import os
import random
import base64
import hashlib
import flag
import messages

KEY = os.urandom(16)
### Always use a cryptographic secure function to generate random nonce
NONCE = hashlib.sha256(KEY).hexdigest()[:16]

FLAG = flag.FLAG
assert FLAG.startswith("CSCPT{") and FLAG.endswith("}")
assert len(FLAG) == 48

MESSAGES = messages.MESSAGES
assert all(b"Cristiano Ronaldo" in msg for msg in MESSAGES)

def encrypt(msg):
    ctr = Counter.new(
        64,
        prefix=bytes.fromhex(NONCE),
        initial_value=0
    )

    cipher = AES.new(KEY, AES.MODE_CTR, counter=ctr)
    return cipher.encrypt(msg)

ciphertexts = []

for msg in MESSAGES:
    prefix = os.urandom(random.randint(0, 32))
    ciphertext = encrypt(prefix + msg)
    ciphertexts.append(base64.b64encode(ciphertext).decode())

with open("ciphertexts.txt", "w") as f:
    for ct in ciphertexts:
        f.write(f"{ct}\n")

print("ciphertexts.txt generated")