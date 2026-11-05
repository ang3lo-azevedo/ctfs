#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def solve():
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # Rotate 3 times to get 4 keys
    for _ in range(3):
        io.sendlineafter(b'Your choice: ', b'1')
        io.recvuntil(b'rotated.')
    
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
    
    print(f"Got {len(keys)} keys")
    print(f"Nonce: {nonce_hex}")
    
    # Split message into 4 parts
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create 4 different ciphertexts, one for each key
    # Each ciphertext, when decrypted with its corresponding key,
    # should have the right chunk at the right position
    
    ciphertexts = []
    for i in range(4):
        # Create a 64-byte plaintext
        # At position [16*i:16*(i+1)], put the correct part
        # The rest can be anything (we'll use spaces)
        plaintext = bytearray(64)
        chunk = parts[i].encode().ljust(16, b' ')
        plaintext[16*i:16*(i+1)] = chunk
        
        # Encrypt with the corresponding key
        ct = AESGCMSIV(keys[i]).encrypt(nonce, bytes(plaintext), b"")
        ciphertexts.append(ct)
        
        print(f"CT[{i}] for key[{i}]: {ct.hex()[:40]}...")
    
    # Now try to push all 4 ciphertexts
    for i, ct in enumerate(ciphertexts):
        print(f"\nPushing ciphertext {i+1}/4...")
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
        
        # Check if we got kicked out
        try:
            response = io.recvuntil(b'Your choice: ', timeout=2)
            if b'cannot remember' in response:
                print(f"Server rejected ciphertext #{i+1} - limit reached")
                break
            else:
                print(f"Ciphertext #{i+1} accepted!")
        except:
            print(f"Connection issue after ciphertext #{i+1}")
            break
    
    # Debug to see how many we got in
    io.sendline(b'2')
    debug = io.recvuntil(b'Your choice: ', timeout=2).decode()
    print(f"\nDebug output:\n{debug}")
    
    # Now request the flag
    print("\nRequesting flag...")
    io.sendline(b'4')
    response = io.recvall(timeout=2).decode()
    print(f"Response:\n{response}")
    
    io.close()

if __name__ == '__main__':
    solve()
