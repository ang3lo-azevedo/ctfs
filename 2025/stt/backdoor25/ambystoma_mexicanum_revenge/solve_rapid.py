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
    
    print(f"Keys: {[k.hex() for k in keys]}")
    print(f"Nonce: {nonce_hex}\n")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create 4 ciphertexts
    ciphertexts = []
    for i in range(4):
        plaintext = bytearray(64)
        chunk = parts[i].encode().ljust(16, b' ')
        plaintext[16*i:16*(i+1)] = chunk
        ct = AESGCMSIV(keys[i]).encrypt(nonce, bytes(plaintext), b"")
        ciphertexts.append(ct.hex())
    
    # Try a different approach: send ALL commands at once without waiting
    print("Sending all commands in rapid succession...")
    
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ciphertexts[0].encode())
    
    # Immediately send more commands before it can break
    io.sendline(b'3')  # Don't wait for prompt
    io.sendline(ciphertexts[1].encode())
    io.sendline(b'3')
    io.sendline(ciphertexts[2].encode())
    io.sendline(b'3')
    io.sendline(ciphertexts[3].encode())
    io.sendline(b'4')  # Request flag
    
    # Now see what we get
    response = io.recvall(timeout=3).decode()
    print(f"\nResponse:\n{response}")
    
    if "flag{" in response:
        print("\n🎉 GOT THE FLAG!")
    
    io.close()

if __name__ == '__main__':
    solve()
