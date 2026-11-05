import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

key = bytes.fromhex('8a4a35876563f1ea8baad6cda0099c24d53d4ce5670b3b23b13063127611bb37')
iv = bytes.fromhex('c0a675360817d8dba62cc79e2fa77734')

with open('object.dat', 'rb') as f:
    encrypted_data = f.read()

cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
decryptor = cipher.decryptor()
pt = decryptor.update(encrypted_data) + decryptor.finalize()

with open('decrypted_object.bin', 'wb') as f:
    f.write(pt)
print("decrypted object.dat to decrypted_object.bin")