#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

# Test: What if the server is ACTUALLY running code with CIPHERTEXTS_LEN = 4?
# The "revenge" might be that the provided source is a red herring!

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
    
    print(f"Keys: {len(keys)}")
    print(f"Nonce: {nonce_hex}\n")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # What if CIPHERTEXTS_LEN is actually 4 on the server?
    # Then we need to push 4 separate ciphertexts, but we haven't been able to...
    
    # OR... what if the file we have is wrong and the server uses i % len(KEYS)?
    # Then we only need 1 ciphertext and 1 key!
    
    # Let me test the 1-key approach more thoroughly
    print("Testing if server uses original (modulo) key indexing...")
    
    # Use only the FIRST key, like the original challenge
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    ct = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
    
    # Test locally what this produces with the revenge code
    print("\nLocal test with revenge code (KEYS[i]):")
    for i in range(4):
        try:
            dec = AESGCMSIV(keys[i]).decrypt(nonce, ct, b"")
            chunk = dec[16*i:16*(i+1)].decode('utf-8').strip()
            print(f"  Key[{i}]: '{chunk}'")
        except:
            print(f"  Key[{i}]: FAIL")
    
    # Test locally what this produces with original code (KEYS[i % 1])
    print("\nLocal test with original code (KEYS[i % len]):")
    for i in range(4):
        try:
            dec = AESGCMSIV(keys[i % len([keys[0]])]).decrypt(nonce, ct, b"")
            chunk = dec[16*i:16*(i+1)].decode('utf-8').strip()
            print(f"  Key[{i % 1}]: '{chunk}'")
        except:
            print(f"  Key[{i}]: FAIL")
    
    # Push it and try
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
    io.sendlineafter(b'Your choice: ', b'4')
    
    resp = io.recvall(timeout=2).decode()
    print(f"\nServer response:\n{resp}")
    
    if "flag{" in resp:
        print("\n🎉 SERVER IS RUNNING ORIGINAL CODE!")
    
    io.close()

if __name__ == '__main__':
    solve()
