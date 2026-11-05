import pefile
import re

pe = pefile.PE('chromelevator.exe')

print("[+] Crypto API Imports:")
try:
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        if b'crypt' in entry.dll.lower() or b'advapi32' in entry.dll.lower():
            for imp in entry.imports:
                if imp.name and (b'Crypt' in imp.name or b'BCrypt' in imp.name):
                    print(f"  - {imp.name.decode('utf-8')}")
except Exception as e:
    print("  [-] Error parsing imports")

with open('chromelevator.exe', 'rb') as f:
    data = f.read()

# Search for BCRYPT_KEY_DATA_BLOB (MDBK + Version 1 + Size 32 or 16)
# 4D 44 42 4B 01 00 00 00 20 00 00 00 (32 bytes / AES-256)
# 4D 44 42 4B 01 00 00 00 10 00 00 00 (16 bytes / AES-128)
match_256 = re.search(b'\x4D\x44\x42\x4B\x01\x00\x00\x00\x20\x00\x00\x00(.{32})', data, re.DOTALL)
match_128 = re.search(b'\x4D\x44\x42\x4B\x01\x00\x00\x00\x10\x00\x00\x00(.{16})', data, re.DOTALL)

print("\n[+] Hardcoded Key Search:")
if match_256:
    print(f"  - Found AES-256 Key: {match_256.group(1).hex()}")
elif match_128:
    print(f"  - Found AES-128 Key: {match_128.group(1).hex()}")
else:
    print("  [-] No standard BCRYPT key blobs found.")