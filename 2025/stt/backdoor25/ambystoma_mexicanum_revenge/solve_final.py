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
    io.recvuntil(b'nonce=')
    nonce_hex = io.recvline().decode().strip()
    
    keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
    keys_hex = keys_str.split(',')
    keys = [binascii.unhexlify(k) for k in keys_hex]
    nonce = binascii.unhexlify(nonce_hex)
    
    print(f"Got {len(keys)} keys")
    print(f"Nonce: {nonce_hex}\n")
    
    # Split message into 4 parts
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create 4 ciphertexts, each encrypting a 64-byte plaintext where
    # the correct chunk is at position [16*i:16*(i+1)]
    ciphertexts = []
    for i in range(4):
        # Create plaintext with the correct part at the right position
        plaintext = bytearray(64)
        chunk = parts[i].encode().ljust(16, b' ')
        plaintext[16*i:16*(i+1)] = chunk
        
        # Encrypt with corresponding key
        ct = AESGCMSIV(keys[i]).encrypt(nonce, bytes(plaintext), b"")
        ciphertexts.append(ct.hex())
        print(f"CT[{i}]: {ct.hex()[:50]}...")
    
    # Try to push all 4 ciphertexts and see what happens
    print("\nAttempting to push 4 ciphertexts...")
    for i in range(4):
        print(f"\nPushing CT {i+1}/4...")
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', ciphertexts[i].encode())
        
        # Read response carefully
        try:
            response = io.recvuntil([b'Your choice:', b'cannot remember'], timeout=3)
            if b'cannot remember' in response:
                print(f"❌ Server rejected after {i+1} ciphertext(s)")
                print(f"Server says: {response.decode()}")
                io.close()
                return False
            else:
                print(f"✓ CT {i+1} accepted")
        except EOFError:
            print(f"❌ Connection closed after {i+1} ciphertext(s)")
            io.close()
            return False
    
    # If we got here, all 4 were accepted!
    print("\n✓ All 4 ciphertexts accepted!")
    
    # Check debug to confirm
    io.sendline(b'2')
    debug = io.recvuntil(b'Your choice:').decode()
    print(f"\nDebug:\n{debug}")
    
    # Now request the flag
    print("\nRequesting flag...")
    io.sendline(b'4')
    response = io.recvall(timeout=2).decode()
    print(f"\nResponse:\n{response}")
    
    if "flag{" in response:
        print("\n🎉 SUCCESS!")
        return True
    
    io.close()
    return False

if __name__ == '__main__':
    solve()
