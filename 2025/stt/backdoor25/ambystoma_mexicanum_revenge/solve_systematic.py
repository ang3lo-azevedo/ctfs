#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def get_keys_and_nonce(io):
    """Helper to get keys and nonce from server"""
    io.sendlineafter(b'Your choice: ', b'2')
    io.recvuntil(b'KEYS=')
    keys_line = io.recvline().decode().strip()
    io.recvuntil(b'CIPHERTEXTS=')
    io.recvline()
    io.recvuntil(b'nonce=')
    nonce_hex = io.recvline().decode().strip()
    
    keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
    keys_hex = keys_str.split(',')
    keys = [binascii.unhexlify(k) for k in keys_hex]
    nonce = binascii.unhexlify(nonce_hex)
    
    return keys, nonce

def attempt_1():
    """Try encrypting full 64-byte message with first key only (like original challenge)"""
    print("\n" + "="*60)
    print("ATTEMPT 1: Use only first key (no rotation)")
    print("="*60)
    
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    keys, nonce = get_keys_and_nonce(io)
    print(f"Got {len(keys)} key(s)")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    
    ct = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
    
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
    
    io.sendlineafter(b'Your choice: ', b'4')
    resp = io.recvall(timeout=1).decode()
    print(f"Response: {resp}")
    io.close()
    
    return "flag{" in resp

def attempt_2():
    """Try encrypting with all 4 keys in a specific pattern"""
    print("\n" + "="*60)
    print("ATTEMPT 2: Rotate 3 times, encrypt with key[0]")
    print("="*60)
    
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    for _ in range(3):
        io.sendlineafter(b'Your choice: ', b'1')
        io.recvuntil(b'Key rotated.')
    
    keys, nonce = get_keys_and_nonce(io)
    print(f"Got {len(keys)} keys")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    
    # Try encrypting with first key
    ct = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
    
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
    
    io.sendlineafter(b'Your choice: ', b'4')
    resp = io.recvall(timeout=1).decode()
    print(f"Response: {resp}")
    io.close()
    
    return "flag{" in resp

def attempt_3():
    """Try each key individually"""
    for key_idx in range(4):
        print(f"\n" + "="*60)
        print(f"ATTEMPT 3.{key_idx}: Encrypt with key[{key_idx}]")
        print("="*60)
        
        io = remote('remote.infoseciitr.in', 4005)
        io.recvuntil(b'one key at a time...')
        
        for _ in range(3):
            io.sendlineafter(b'Your choice: ', b'1')
            io.recvuntil(b'Key rotated.')
        
        keys, nonce = get_keys_and_nonce(io)
        
        parts = ["gib m", "e fl", "ag p", "lis"]
        plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
        
        ct = AESGCMSIV(keys[key_idx]).encrypt(nonce, plaintext, b"")
        
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
        
        io.sendlineafter(b'Your choice: ', b'4')
        resp = io.recvall(timeout=1).decode()
        print(f"Response: {resp}")
        
        if "flag{" in resp:
            print(f"\nSUCCESS with key[{key_idx}]!")
            io.close()
            return True
        
        io.close()
    
    return False

if __name__ == '__main__':
    if attempt_1():
        print("\n✓ Attempt 1 worked!")
    elif attempt_2():
        print("\n✓ Attempt 2 worked!")
    elif attempt_3():
        print("\n✓ Attempt 3 worked!")
    else:
        print("\n✗ All attempts failed. Need a different approach.")
