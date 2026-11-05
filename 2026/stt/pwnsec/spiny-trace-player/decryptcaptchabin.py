import pefile
import glob
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

pe = pefile.PE('decrypted_object.bin')
key = pe.get_data(0x1b440, 32)

files = glob.glob('*captcha.bin*')
with open(files[0], 'rb') as f:
    data = f.read()

iv = data[:12]
tag = data[12:28]
ciphertext = data[28:]
aesgcm = AESGCM(key)
decrypted = aesgcm.decrypt(iv, ciphertext + tag, None)

with open('decrypted_captcha.bin', 'wb') as f:
    f.write(decrypted)
print("decrypted captcha.bin to decrypted_captcha.bin")