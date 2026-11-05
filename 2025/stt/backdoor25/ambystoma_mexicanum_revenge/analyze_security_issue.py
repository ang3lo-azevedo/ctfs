#!/usr/bin/env python3
"""
Systematic analysis to find the security vulnerability in the challenge code.
Based on documentation, AESGCMSIV doesn't explicitly warn against nonce reuse
unlike other AEAD modes (ChaCha20Poly1305, AESGCM, AESOCB3, AESCCM all say "NEVER REUSE").

This is suspicious - let's investigate why.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
import os
import binascii

print("="*80)
print("SECURITY ISSUE ANALYSIS: AES-GCM-SIV Nonce Reuse")
print("="*80)

# Key observation: GCM-SIV is specifically designed to be nonce-misuse resistant
# This means reusing a nonce doesn't catastrophically break security like in regular GCM
# BUT it has a specific property we can exploit

print("\n1. Testing GCM-SIV with nonce reuse:")
print("-" * 60)

nonce = os.urandom(12)
print(f"Shared nonce: {nonce.hex()}")

# Create 4 different keys
keys = [os.urandom(16) for _ in range(4)]
for i, key in enumerate(keys):
    print(f"Key {i}: {key.hex()}")

# The security issue might be in how the service handles decryption failures
# Let's trace through the exact code path

print("\n2. Simulating exact challenge behavior:")
print("-" * 60)

class Service:
    def __init__(self):
        self.key = os.urandom(16)
        self.nonce = os.urandom(12)  # NEVER CHANGES - this is the vulnerability
        self.aad = b""
    
    def decrypt(self, ciphertext, key):
        try:
            plaintext = AESGCMSIV(key).decrypt(self.nonce, ciphertext, self.aad)
            return plaintext
        except Exception:
            return None

service = Service()
print(f"Service nonce (fixed): {service.nonce.hex()}")

# Now here's the critical insight:
# The challenge code does: text = service.decrypt(ct, key)[16 * i:16 * (i+1)]
# It slices AFTER decryption
# What if the ciphertext is structured such that slicing gives us different parts?

print("\n3. Testing ciphertext structure exploitation:")
print("-" * 60)

# Build a 64-byte plaintext (4 x 16 bytes)
target = b"gib me flag plis"
plaintext = target * 4  # "gib me flag plis" repeated 4 times
print(f"Target plaintext (64 bytes): {plaintext}")

# Encrypt with the FIRST key (service.key) using service nonce
ct = AESGCMSIV(service.key).encrypt(service.nonce, plaintext, service.aad)
print(f"\nCiphertext (hex): {binascii.hexlify(ct).decode()}")
print(f"Ciphertext length: {len(ct)} bytes (64 + 16 tag = 80 bytes)")

# Now try to decrypt with the SAME key and slice
print("\n4. Testing decryption and slicing with CORRECT key:")
print("-" * 60)
for i in range(4):
    decrypted = service.decrypt(ct, service.key)
    if decrypted:
        slice_data = decrypted[16 * i:16 * (i+1)]
        print(f"Slice {i} [16*{i}:16*{i+1}]: {slice_data}")
    else:
        print(f"Slice {i}: Decryption failed")

# THE KEY INSIGHT: The challenge rotates keys but keeps the SAME nonce
# In the challenge, we need ONE ciphertext that works with ALL keys
# This is normally impossible...

print("\n5. THE VULNERABILITY:")
print("-" * 60)
print("The challenge expects ONE ciphertext to decrypt successfully with 4 DIFFERENT keys.")
print("This violates the fundamental property of authenticated encryption.")
print()
print("HOWEVER, notice the code flow:")
print("- service.nonce is set ONCE in __init__ and never changes")
print("- service.key rotates with gen_key()")
print("- decrypt() uses self.nonce (class instance variable)")
print()
print("But wait... in decrypt(), we do:")
print("  AESGCMSIV(key).decrypt(self.nonce, ciphertext, self.aad)")
print()
print("We're creating a NEW AESGCMSIV instance with the passed 'key' parameter")
print("but using self.nonce from the service instance!")
print()
print("The security issue is: Can we find a ciphertext that happens to")
print("authenticate correctly with multiple different keys when using the")
print("same nonce? This is a collision attack on the authentication tag.")

print("\n6. Checking if this is even theoretically possible:")
print("-" * 60)
print("AES-GCM-SIV authentication tag is 128 bits (16 bytes)")
print("Probability of random collision: 2^-128 (practically impossible)")
print()
print("BUT - if there's a weakness in the implementation or a related-key")
print("attack, or if the challenge has a backdoor/specific property...")
print()
print("Let's check if we can brute force a collision for small key spaces...")

# Actually, wait - let me re-read the challenge more carefully
print("\n7. RE-ANALYZING THE CHALLENGE CODE:")
print("-" * 60)
print("Line 86: key = binascii.unhexlify(KEYS[i])")
print("Line 87: ct = binascii.unhexlify(CIPHERTEXTS[i % len(CIPHERTEXTS)])")
print("Line 88: text = service.decrypt(ct, key)[16 * i:16 * (i+1)].decode('utf-8').strip()")
print()
print("With CIPHERTEXTS_LEN=1, we have ONE ciphertext.")
print("The same ciphertext is used for i=0,1,2,3")
print("But DIFFERENT keys are used: KEYS[0], KEYS[1], KEYS[2], KEYS[3]")
print()
print("The slicing [16*i:16*(i+1)] means:")
print("  i=0: [0:16]   - first 16 bytes")
print("  i=1: [16:32]  - second 16 bytes")
print("  i=2: [32:48]  - third 16 bytes")  
print("  i=3: [48:64]  - fourth 16 bytes")
print()
print("So we need a ciphertext that:")
print("1. Decrypts with key[0] to give plaintext, bytes [0:16] = 'gib me flag plis'")
print("2. Decrypts with key[1] to give plaintext, bytes [16:32] = 'gib me flag plis'")
print("3. Decrypts with key[2] to give plaintext, bytes [32:48] = 'gib me flag plis'")
print("4. Decrypts with key[3] to give plaintext, bytes [48:64] = 'gib me flag plis'")
print()
print("This is IMPOSSIBLE with standard AES-GCM-SIV because:")
print("- Authentication will fail if wrong key is used")
print("- A ciphertext can only authenticate with ONE key")

print("\n8. CONCLUSION - WHERE IS THE VULNERABILITY?")
print("-" * 60)
print("The vulnerability must be one of:")
print()
print("A) Implementation bug in cryptography library version 46.0.3")
print("   - Allows authentication bypass somehow")
print("   - Related to nonce reuse edge case")
print()
print("B) Mathematical property of GCM-SIV we haven't discovered")
print("   - Some related-key attack")
print("   - Nonce reuse with multiple keys creates exploitable state")
print()
print("C) The challenge is actually impossible as coded")
print("   - Author made a mistake")
print("   - Or server runs different code")
print()
print("D) There's a trick in how Python/the library handles errors")
print("   - Exception swallowing that allows partial success")
print("   - Timing-based attack")

print("\n9. TESTING HYPOTHESIS: Check cryptography library source")
print("-" * 60)

# Let's check if there's any known issue with version 46.0.3
import cryptography
print(f"Cryptography version: {cryptography.__version__}")
print()
print("Need to research if version 46.0.3 has any known vulnerabilities")
print("related to AES-GCM-SIV nonce reuse or authentication bypass...")
