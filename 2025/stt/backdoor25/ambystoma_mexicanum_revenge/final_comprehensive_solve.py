#!/usr/bin/env python3
"""
Final comprehensive solve attempt for Ambystoma Mexicanum Revenge.

This script documents all the constraints and attempts the most logical solution,
even though it appears cryptographically impossible.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def comprehensive_solve():
    log.info("Connecting to server...")
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # STEP 1: Generate 4 keys by rotating 3 times
    log.info("Rotating keys to generate 4 keys...")
    for i in range(3):
        io.sendlineafter(b'Your choice: ', b'1')
        io.recvuntil(b'rotated.')
        log.success(f"Rotation {i+1}/3 complete")
    
    # STEP 2: Extract keys and nonce via debug
    log.info("Extracting keys and nonce...")
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
    
    log.success(f"Extracted {len(keys)} keys")
    log.info(f"Keys: {keys_hex}")
    log.info(f"Nonce: {nonce_hex}")
    
    # STEP 3: Analyze what we need
    log.info("\nAnalyzing requirements...")
    log.info("Target message: 'gib me flag plis' (16 characters)")
    log.info("Split into 4 parts: ['gib m', 'e fl', 'ag p', 'lis']")
    log.info("Server will:")
    log.info("  - Use CIPHERTEXTS[i % 1] = CIPHERTEXTS[0] for all i")
    log.info("  - Decrypt with KEYS[i] for i in [0, 1, 2, 3]")
    log.info("  - Extract bytes[16*i:16*(i+1)] from each decryption")
    log.info("  - Concatenate after stripping")
    
    #  STEP 4: The core problem
    log.warn("\nCORE PROBLEM: We need ONE ciphertext that:")
    log.warn("  - Decrypts successfully with keys[0] AND")
    log.warn("  - Decrypts successfully with keys[1] AND")
    log.warn("  - Decrypts successfully with keys[2] AND")
    log.warn("  - Decrypts successfully with keys[3]")
    log.warn("This is cryptographically infeasible with AES-GCM-SIV!")
    
    # STEP 5: Try the "impossible" solution anyway
    log.info("\nAttempting solution despite impossibility...")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create plaintext where each chunk has the right part
    plaintext = b"".join(p.encode().ljust(16, b' ') for p in parts)
    log.info(f"Plaintext (64 bytes): {repr(plaintext)}")
    
    # Try encrypting with each key and testing
    for key_idx in range(4):
        log.info(f"\n--- Attempt with key[{key_idx}] ---")
        ct = AESGCMSIV(keys[key_idx]).encrypt(nonce, plaintext, b"")
        log.info(f"Ciphertext: {ct.hex()[:60]}...")
        
        # Test locally what each key produces
        log.info("Local simulation:")
        all_pass = True
        for i in range(4):
            try:
                dec = AESGCMSIV(keys[i]).decrypt(nonce, ct, b"")
                chunk = dec[16*i:16*(i+1)].decode('utf-8').strip()
                expected = parts[i]
                status = "✓" if chunk == expected else "✗"
                log.info(f"  {status} Key[{i}]: '{chunk}' (expected: '{expected}')")
                if chunk != expected:
                    all_pass = False
            except Exception as e:
                log.error(f"  ✗ Key[{i}]: DECRYPT FAILED")
                all_pass = False
        
        if all_pass:
            log.success(f"\n🎉 KEY[{key_idx}] WORKS FOR ALL DECRYPTIONS!")
            log.info("Submitting to server...")
            
            io.sendlineafter(b'Your choice: ', b'3')
            io.sendlineafter(b'Enter ciphertext (hex): ', ct.hex().encode())
            io.sendlineafter(b'Your choice: ', b'4')
            
            resp = io.recvall(timeout=3).decode()
            log.info(f"\nServer response:\n{resp}")
            
            if "flag{" in resp:
                log.success("\n🎉🎉🎉 GOT THE FLAG! 🎉🎉🎉")
                flag_start = resp.index("flag{")
                flag_end = resp.index("}", flag_start) + 1
                flag = resp[flag_start:flag_end]
                log.success(f"\nFLAG: {flag}")
                io.close()
                return True
            
            io.close()
            return False
    
    log.error("\n❌ No key worked for all 4 decryptions")
    log.error("This challenge appears to require a non-standard solution")
    io.close()
    return False

if __name__ == '__main__':
    success = comprehensive_solve()
    if not success:
        log.error("\n" + "="*60)
        log.error("CHALLENGE UNSOLVED")
        log.error("="*60)
        log.error("Possible reasons:")
        log.error("1. Server code differs from provided source")
        log.error("2. Crypto library vulnerability exists")
        log.error("3. Non-cryptographic exploit required")
        log.error("4. Challenge may be broken")
