#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def solve_assuming_4_cts():
    """
    This solution ASSUMES the server has CIPHERTEXTS_LEN = 4 (or higher),
    allowing us to push 4 different ciphertexts.
    """
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
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create 4 cipher texts, each for its corresponding key
    # CT[i] when decrypted with key[i] should have the right part at position [16*i:16*(i+1)]
    ciphertexts = []
    for i in range(4):
        # Create a 64-byte plaintext
        plaintext = bytearray(64)
        # Put the correct part at the correct position
        chunk = parts[i].encode().ljust(16, b' ')
        plaintext[16*i:16*(i+1)] = chunk
        
        # Encrypt with the corresponding key
        ct = AESGCMSIV(keys[i]).encrypt(nonce, bytes(plaintext), b"")
        ciphertexts.append(ct.hex())
        print(f"CT[{i}] ({len(ct.hex())} hex chars): {ct.hex()[:50]}...")
    
    # Try pushing all 4, monitoring carefully for when/if it breaks
    print("\nPushing ciphertexts...")
    for i in range(4):
        print(f"\nPushing CT #{i+1}...")
        try:
            io.sendlineafter(b'Your choice: ', b'3', timeout=3)
            io.sendlineafter(b'Enter ciphertext (hex): ', ciphertexts[i].encode(), timeout=3)
            
            # Wait for response
            resp = io.recvuntil([b'Your choice:', b'cannot remember'], timeout=3)
            
            if b'cannot remember' in resp:
                print(f"❌ Server rejected at CT #{i+1}")
                print("The server's CIPHERTEXTS_LEN is NOT 4 or higher")
                io.close()
                return False
            elif b'Your choice:' in resp:
                print(f"✓ CT #{i+1} accepted!")
        except Exception as e:
            print(f"❌ Error at CT #{i+1}: {e}")
            io.close()
            return False
    
    print("\n✅ All 4 ciphertexts accepted! The server allows 4+ ciphertexts!")
    
    # Debug to verify
    io.sendline(b'2')
    debug = io.recvuntil(b'Your choice:', timeout=3).decode()
    print(f"\nDebug output:\n{debug}")
    
    # Request the flag
    print("\nRequesting flag...")
    io.sendline(b'4')
    resp = io.recvall(timeout=3).decode()
    print(f"\nResponse:\n{resp}")
    
    if "flag{" in resp:
        print("\n🎉🎉🎉 GOT THE FLAG! 🎉🎉🎉")
        # Extract and display the flag
        flag_start = resp.index("flag{")
        flag_end = resp.index("}", flag_start) + 1
        flag = resp[flag_start:flag_end]
        print(f"\nFLAG: {flag}")
        return True
    
    io.close()
    return False

if __name__ == '__main__':
    success = solve_assuming_4_cts()
    if not success:
        print("\n❌ This approach didn't work. The server's CIPHERTEXTS_LEN appears to be 1.")
