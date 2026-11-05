#!/usr/bin/env python3
"""
Wait - I need to reconsider the ENTIRE problem from scratch.

The service creates ONE instance with ONE nonce.
We rotate keys 3 times to get 4 keys.
ALL encryptions/decryptions use the SAME nonce from that ONE service instance.

What if the solution is simpler than I thought?
Let me trace through EXACTLY what happens.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
import os

# Simulate the exact server behavior
class Service:
    def __init__(self):
        self.key = os.urandom(16)
        self.nonce = os.urandom(12)  # ONE NONCE, NEVER CHANGES
        self.aad = b""
        print(f"Service initialized with nonce: {self.nonce.hex()}")

    def gen_key(self):
        self.key = os.urandom(16)
        return self.key
    
    def decrypt(self, ciphertext, key):
        try:
            plaintext = AESGCMSIV(key).decrypt(self.nonce, ciphertext, self.aad)
            return plaintext
        except Exception:
            return None

# Simulate the challenge
service = Service()
KEYS = [service.key.hex()]

print("\nRotating keys...")
for i in range(3):
    service.gen_key()
    KEYS.append(service.key.hex())
    print(f"  Key {i+1}: {KEYS[i+1][:16]}...")

print(f"\nWe now have {len(KEYS)} keys")
print(f"Service nonce (NEVER CHANGED): {service.nonce.hex()}")
print(f"Service current key: {service.key.hex()}")

# The challenge: create ONE ciphertext that works with all 4 keys
print("\n" + "="*60)
print("CHALLENGE: One CT must decrypt with 4 different keys")
print("All using the SAME nonce")
print("="*60)

# Let me think... what if we encrypt with the LAST key (service.key)?
# That's the current state of the service object!

print("\nWait! service.key is the LAST rotated key!")
print(f"service.key = KEYS[3] = {service.key.hex() == KEYS[3]}")

# What if the solution uses the SERVICE's current key somehow?
parts = ["gib m", "e fl", "ag p", "lis"]
plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)

print("\nEncrypting with service.key (the CURRENT key)...")
ct = AESGCMSIV(service.key).encrypt(service.nonce, plaintext, service.aad)

print("Testing decryption with all 4 keys:")
import binascii
for i in range(4):
    key = binascii.unhexlify(KEYS[i])
    result = service.decrypt(ct, key)
    if result:
        chunk = result[16*i:16*(i+1)].decode('utf-8').strip()
        print(f"  Key[{i}]: '{chunk}'")
    else:
        print(f"  Key[{i}]: FAILED")

print("\n" + "="*60)
print("Still doesn't work - wrong keys can't decrypt")
print("="*60)
