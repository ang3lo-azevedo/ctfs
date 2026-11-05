#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def solve():
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # Rotate 3 times
    for _ in range(3):
        io.sendlineafter(b'Your choice: ', b'1')
        io.recvuntil(b'rotated.')
    
    # Get keys and nonce
    io.sendlineafter(b'Your choice: ', b'2')
    io.recvuntil(b'KEYS=')
    keys_line = io.recvline().decode().strip()
    io.recvuntil(b'nonce=')
    nonce_hex = io.recvline().decode().strip()
    
    keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
    keys_hex = keys_str.split(',')
    keys = [binascii.unhexlify(k) for k in keys_hex]
    nonce = binascii.unhexlify(nonce_hex)
    
    print(f"Keys: {keys_hex}")
    print(f"Nonce: {nonce_hex}\n")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create one ciphertext
    plaintext = bytearray(64)
    chunk = parts[0].encode().ljust(16, b' ')
    plaintext[0:16] = chunk
    ct = AESGCMSIV(keys[0]).encrypt(nonce, bytes(plaintext), b"")
    
    # Push first ciphertext  
    print("Pushing ciphertext 1...")
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
    
    # Try to read what happens
    response1 = io.recvuntil(b'Your choice: ', timeout=2).decode()
    print(f"After CT 1:\n{response1}\n")
    
    # Try to push a second one
    print("Pushing ciphertext 2...")
    ct2 = AESGCMSIV(keys[1]).encrypt(nonce, bytes(64), b"")
    io.sendline(b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ct2.hex().encode())
    
    # What happens now?
    response2 = io.recvall(timeout=2).decode()
    print(f"After CT 2:\n{response2}")
    
    io.close()

if __name__ == '__main__':
    solve()
