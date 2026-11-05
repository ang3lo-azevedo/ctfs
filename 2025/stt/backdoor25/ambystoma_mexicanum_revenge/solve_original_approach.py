#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def solve():
    # Maybe the server is actually running the ORIGINAL code?
    # Let's try the original solution: don't rotate, use same key for all
    
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # DON'T rotate - keep just 1 key
    # Get the key and nonce
    io.sendlineafter(b'Your choice: ', b'2')
    io.recvuntil(b'KEYS=')
    keys_line = io.recvline().decode().strip()
    io.recvuntil(b'nonce=')
    nonce_hex = io.recvline().decode().strip()
    
    keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
    keys_hex = keys_str.split(',')
    keys = [binascii.unhexlify(k) for k in keys_hex]
    nonce = binascii.unhexlify(nonce_hex)
    
    print(f"Got {len(keys)} key(s): {keys_hex}")
    print(f"Nonce: {nonce_hex}\n")
    
    # Use the original challenge solution
    parts = ["gib m", "e fl", "ag p", "lis"]
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    
    print(f"Plaintext: {repr(plaintext)}")
    
    # Encrypt with the single key
    ct = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
    print(f"Ciphertext: {ct.hex()[:60]}...\n")
    
    # Push it
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
    
    # Request flag
    io.sendlineafter(b'Your choice: ', b'4')
    response = io.recvall(timeout=2).decode()
    print(f"Response:\n{response}")
    
    if "flag{" in response:
        print("\n🎉 SUCCESS! The server is running the ORIGINAL code!")
    
    io.close()

if __name__ == '__main__':
    solve()
