#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

# Target message: "gib me flag plis"
# We need to split it into 4 chunks of 16 bytes each
REQUEST = "gib me flag plis"

def solve():
    # Connect to the service
    io = remote('remote.infoseciitr.in', 4004)
    # io = process(['python3', 'chall.py'])
    
    # Receive banner
    io.recvuntil(b'one key at a time...')
    
    # Debug to get keys and nonce
    io.sendlineafter(b'Your choice: ', b'2')
    io.recvuntil(b'KEYS=')
    keys_line = io.recvline().decode().strip()
    io.recvuntil(b'CIPHERTEXTS=')
    io.recvline()
    io.recvuntil(b'nonce=')
    nonce_hex = io.recvline().decode().strip()
    
    # Parse keys
    keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
    keys_hex = keys_str.split(',')
    keys = [binascii.unhexlify(k) for k in keys_hex]
    nonce = binascii.unhexlify(nonce_hex)
    
    print(f"Got {len(keys)} keys")
    print(f"Nonce: {nonce_hex}")
    
    # Strategy: Split "gib me flag plis" into 4 chunks where no chunk ends with space
    # This way .strip() won't remove the spaces we need
    # "gib m" + "e fl" + "ag p" + "lis" = "gib me flag plis"
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    plaintext = b""
    for part in parts:
        # Pad to 16 bytes with spaces (which will be stripped from the end)
        plaintext += part.encode().ljust(16, b' ')
    
    print(f"Plaintext length: {len(plaintext)} bytes")
    print(f"Plaintext repr: {repr(plaintext)}")
    
    print("Strategy: Use the same key for all 4 positions")
    print(f"Key 0: {keys[0].hex()}")
    
    # Encrypt with the first key
    aead = AESGCMSIV(keys[0])
    ciphertext = aead.encrypt(nonce, plaintext, b"")
    
    print(f"Ciphertext: {ciphertext.hex()}")
    
    # Test locally if this works
    print("\nTesting locally:")
    usertext = ""
    for i in range(4):
        key = keys[0]  # Use same key for all
        try:
            decrypted = AESGCMSIV(key).decrypt(nonce, ciphertext, b"")
            chunk = decrypted[16 * i:16 * (i+1)].decode('utf-8').strip()
            print(f"Chunk {i}: '{chunk}' (bytes {16*i}:{16*(i+1)})")
            usertext += chunk
        except Exception as e:
            print(f"Error at chunk {i}: {e}")
            break
    
    print(f"Final message: '{usertext}'")
    
    if usertext == REQUEST:
        print("Success! This should work.")
    else:
        print(f"Failed: got '{usertext}' instead of '{REQUEST}'")
    
    if usertext == REQUEST:
        print("Success! This should work.")
        
        # Send the ciphertext to the service
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', ciphertext.hex().encode())
        
        # Request the flag
        io.sendlineafter(b'Your choice: ', b'4')
        
        # Get response
        response = io.recvall(timeout=2).decode()
        print(f"\nServer response:\n{response}")
    else:
        print(f"Failed: got '{usertext}' instead of '{REQUEST}'")
    
    io.close()

if __name__ == '__main__':
    solve()
