#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii
import os

# Target message: "gib me flag plis"
REQUEST = "gib me flag plis"

def test_local():
    """Test with local challenge to understand the behavior"""
    
    # Simulate the service
    KEY_SIZE = 16
    NONCE_SIZE = 12
    
    keys = [os.urandom(KEY_SIZE) for _ in range(4)]
    nonce = os.urandom(NONCE_SIZE)
    
    print("Local simulation:")
    print(f"Keys: {[k.hex() for k in keys]}")
    print(f"Nonce: {nonce.hex()}")
    
    # Split the message
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Try approach: Create a 64-byte plaintext and encrypt with a "master" key
    # that we construct from all 4 keys
    
    # Idea: What if we XOR all the keys together to create a combined key?
    # Then encrypt with that?
    master_key = bytes([k[0] ^ k[1] ^ k[2] ^ k[3] for k in zip(keys[0], keys[1], keys[2], keys[3])])
    print(f"\nMaster key (XOR): {master_key.hex()}")
    
    plaintext = b""
    for part in parts:
        plaintext += part.encode().ljust(16, b' ')
    
    try:
        ciphertext = AESGCMSIV(master_key).encrypt(nonce, plaintext, b"")
        print(f"Ciphertext: {ciphertext.hex()[:40]}...")
        
        # Test decryption with each key
        print("\nDecryption test:")
        for i in range(4):
            try:
                decrypted = AESGCMSIV(keys[i]).decrypt(nonce, ciphertext, b"")
                chunk = decrypted[16*i:16*(i+1)].decode('utf-8').strip()
                print(f"  Key[{i}]: SUCCESS - '{chunk}'")
            except Exception as e:
                print(f"  Key[{i}]: FAILED")
    except Exception as e:
        print(f"Encryption failed: {e}")
    
    # That probably won't work... Let me try another idea
    
    # What if the solution is to find a ciphertext that's so mangled that
    # decryption "succeeds" (doesn't throw) but produces garbage that happens
    # to have our target strings at the right positions?
    
    # Actually, AES-GCM-SIV won't let us decrypt with wrong key at all...
    
    # Let me think about the problem from first principles:
    # The challenge is solvable (presumably), so there must be a solution
    # The only way forward I can see is if:
    # 1. There's a vulnerability in the crypto library
    # 2. The keys have a special relationship (but they're random)
    # 3. There's a side channel or timing attack
    # 4. We're misunderstanding the code
    
    print("\n" + "="*60)
    print("Checking if there's something we missed in the code...")
    print("="*60)
    
    # Let me re-examine the exact decryption call:
    # plaintext = AESGCMSIV(key).decrypt(self.nonce, ciphertext, self.aad)
    #
    # self.aad = b"" (empty Additional Authenticated Data)
    # self.nonce is fixed
    #
    # The decrypt function signature is:
    # decrypt(nonce, data, associated_data)
    
    # Wait... what if we can manipulate the AAD somehow?
    # No, we can't, the service controls that.
    
    # What if we need to exploit the fact that we can see all the keys?
    # Maybe we can use the keys to craft a special ciphertext?
    
    # Actually, you know what? Let me just try encrypting with ALL FOUR keys
    # in sequence and see what happens. Maybe there's AES-CTR mode or something
    # where we can layer encryptions?
    
    print("\nTrying multi-layer encryption:")
    ct = plaintext
    for i in range(4):
        ct = AESGCMSIV(keys[i]).encrypt(nonce, ct, b"")
        print(f"After key[{i}]: len={len(ct)}")
    
    # Now try decrypting in reverse order
    pt = ct
    for i in range(3, -1, -1):
        try:
            pt = AESGCMSIV(keys[i]).decrypt(nonce, pt, b"")
            print(f"After decrypting key[{i}]: len={len(pt)}")
        except Exception as e:
            print(f"Failed at key[{i}]: {e}")
            break
    
    if pt == plaintext:
        print("Multi-layer approach restored original plaintext!")
    else:
        print("Multi-layer didn't work as expected")

if __name__ == '__main__':
    test_local()
