#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def solve():
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # Rotate keys 3 times
    for _ in range(3):
        io.sendlineafter(b'Your choice: ', b'1')
        io.recvuntil(b'Key rotated.')
    
    # Get keys and nonce
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
    
    print(f"Keys: {keys_hex}")
    print(f"Nonce: {nonce_hex}\n")
    
    # New idea: What if we craft 4 separate plaintexts and encrypt each with its key?
    # Then we somehow combine them?
    
    # For iteration i, we need:
    # decrypt(CT, keys[i])[16*i:16*(i+1)] = parts[i]
    
    # What if each key decrypts the ciphertext to a DIFFERENT plaintext?
    # That's how AEAD works - wrong key = decryption failure
    # UNLESS... there's a collision?
    
    # Let me try a brute force approach: try to find a ciphertext that
    # happens to decrypt (or fail gracefully) with all 4 keys
    
    # Actually, AES-GCM-SIV won't let wrong keys decrypt at all...
    
    # Wait, unless... what if we exploit the slicing behavior?
    # If decryption produces a short plaintext, the slice might be empty
    # but .strip() on empty string is still empty string
    # and the check is: if not text or len(text) == 0
    # So empty string would fail the check!
    
    # Hmm, I'm running out of ideas. Let me try submitting something and
    # carefully examine the error message
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    
    # Try encrypting with each key and see what happens
    for key_idx in range(4):
        print(f"\n--- Attempt with key[{key_idx}] ---")
        ct = AESGCMSIV(keys[key_idx]).encrypt(nonce, plaintext, b"")
        
        # Test locally what each key produces
        print(f"Local test for ciphertext encrypted with key[{key_idx}]:")
        for i in range(4):
            try:
                dec = AESGCMSIV(keys[i]).decrypt(nonce, ct, b"")
                chunk = dec[16*i:16*(i+1)].decode('utf-8', errors='replace').strip()
                print(f"  Key[{i}] -> '{chunk}'")
            except:
                print(f"  Key[{i}] -> FAIL")
        
        # Try submitting this one
        print(f"\nSubmitting to server...")
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
        
        io.sendlineafter(b'Your choice: ', b'4')
        resp = io.recvall(timeout=1).decode()
        print(f"Response: {resp}")
        
        if "flag" in resp:
            print(f"\n{'='*60}")
            print(f"SUCCESS WITH KEY[{key_idx}]!")
            print(f"{'='*60}")
            break
        else:
            # Reconnect for next attempt
            io.close()
            if key_idx < 3:
                io = remote('remote.infoseciitr.in', 4005)
                io.recvuntil(b'one key at a time...')
                for _ in range(3):
                    io.sendlineafter(b'Your choice: ', b'1')
                    io.recvuntil(b'Key rotated.')
    
    io.close()

if __name__ == '__main__':
    solve()
