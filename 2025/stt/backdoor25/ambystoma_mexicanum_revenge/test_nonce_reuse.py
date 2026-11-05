#!/usr/bin/env python3
"""
BREAKTHROUGH: The service reuses the SAME nonce for all encryptions!

In AES-GCM-SIV, even though it's designed to be nonce-misuse resistant,
there are still exploitable properties when the same nonce is used with
DIFFERENT keys.

The key insight: AES-GCM-SIV uses the nonce in a specific way during
encryption. With the same nonce but different keys, there might be
a way to construct a ciphertext that "works" with multiple keys.

Let me test if we can exploit the nonce reuse property.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii
import os

def test_nonce_reuse_exploit():
    """
    Test if we can construct a special ciphertext using the nonce reuse property.
    
    Key observation: In GCM-SIV, the authentication tag is computed using:
    - A polynomial hash of the plaintext and AAD
    - The nonce
    - The key
    
    With the same nonce but different keys, we might be able to find
    a ciphertext that validates with multiple keys through careful construction.
    """
    
    # Simulate the server setup
    nonce = os.urandom(12)
    keys = [os.urandom(16) for _ in range(4)]
    
    print("Testing nonce reuse exploitation...")
    print(f"Nonce: {nonce.hex()}")
    print(f"Keys: {[k.hex() for k in keys]}\n")
    
    # The target message parts
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Strategy 1: Try encrypting with a "combined" approach
    # What if we encrypt the FULL message with the FIRST key,
    # and the fact that the nonce is reused allows some exploitation?
    
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    print(f"Target plaintext: {repr(plaintext)}\n")
    
    # Encrypt with key[0]
    ct = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
    print(f"Ciphertext (encrypted with key[0]): {ct.hex()[:60]}...\n")
    
    # Test if by some miracle it works with other keys
    print("Testing decryption with all keys:")
    for i, key in enumerate(keys):
        try:
            dec = AESGCMSIV(key).decrypt(nonce, ct, b"")
            chunk = dec[16*i:16*(i+1)].decode('utf-8').strip()
            print(f"  Key[{i}]: SUCCESS - chunk at [{16*i}:{16*(i+1)}] = '{chunk}'")
        except Exception as e:
            print(f"  Key[{i}]: FAILED - {type(e).__name__}")
    
    print("\n" + "="*60)
    print("Strategy 1 failed (as expected)")
    print("="*60)
    
    # Strategy 2: What if the nonce reuse means we should NOT rotate keys?
    # Maybe with a single key and nonce reuse, there's a special property?
    
    print("\nStrategy 2: Test with single key (no rotation)")
    single_key = keys[0]
    
    # Encrypt multiple times with same key and nonce
    ct1 = AESGCMSIV(single_key).encrypt(nonce, plaintext, b"")
    ct2 = AESGCMSIV(single_key).encrypt(nonce, plaintext, b"")
    
    print(f"CT1: {ct1.hex()[:40]}...")
    print(f"CT2: {ct2.hex()[:40]}...")
    print(f"Same? {ct1 == ct2}")
    
    # In GCM-SIV, encryption is DETERMINISTIC!
    # Same key + nonce + plaintext = same ciphertext!
    
    if ct1 == ct2:
        print("\n✓ GCM-SIV is DETERMINISTIC with nonce reuse!")
        print("This means: same (key, nonce, plaintext) -> same ciphertext")
    
    print("\n" + "="*60)
    print("Key insight: GCM-SIV deterministic encryption with nonce reuse")
    print("But we still need to decrypt with 4 DIFFERENT keys...")
    print("="*60)

if __name__ == '__main__':
    test_nonce_reuse_exploit()
