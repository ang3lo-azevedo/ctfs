#!/usr/bin/env python3
from pwn import *

io = remote('remote.infoseciitr.in', 4005)
io.recvuntil(b'one key at a time...')

# Just try pushing multiple dummy ciphertexts to find the exact limit
for i in range(1, 6):
    print(f"\nAttempting to push ciphertext #{i}...")
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', b'00' * 80)  # Dummy CT
    
    # Try to get the next prompt
    try:
        resp = io.recvuntil([b'Your choice:', b'cannot remember'], timeout=2)
        if b'cannot remember' in resp:
            print(f"❌ Limit reached at ciphertext #{i}")
            print(f"So CIPHERTEXTS_LEN = {i-1}")
            break
        elif b'Your choice:' in resp:
            print(f"✓ Ciphertext #{i} accepted")
    except EOFError:
        print(f"❌ Connection closed at ciphertext #{i}")
        break

io.close()
