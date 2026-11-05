#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def solve():
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # DON'T rotate keys - keep just 1 key
    # DON'T push any ciphertext
    # Just request the flag
    
    print("Attempting without pushing ciphertext...")
    io.sendlineafter(b'Your choice: ', b'4')
    
    resp = io.recvall(timeout=2).decode()
    print(f"Response:\n{resp}")
    
    io.close()

if __name__ == '__main__':
    solve()
