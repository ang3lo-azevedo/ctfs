#!/usr/bin/env python3
from pwn import *

io = remote('remote.infoseciitr.in', 4005)
io.recvuntil(b'one key at a time...')

# Try injecting Python code through the hex input
# The input goes through: input() -> .strip() -> CIPHERTEXTS.append() -> later binascii.unhexlify()

# Can we break out of the hex string somehow?
malicious_inputs = [
    "'; import os; os.system('ls'); '",  # Try code injection
    "__import__('os').system('ls')",  # Another injection attempt
    "\\x00" * 100,  # Null bytes
    "A" * 100000,  # Very long string
]

for inp in malicious_inputs:
    print(f"\nTrying: {inp[:50]}...")
    try:
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', inp.encode())
        resp = io.recvuntil(b'Your choice: ', timeout=2)
        print(f"Response: {resp[:100]}")
    except:
        print("Connection died")
        break

io.close()
