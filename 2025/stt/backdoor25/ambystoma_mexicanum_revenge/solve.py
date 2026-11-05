#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

# Target message: "gib me flag plis"
REQUEST = "gib me flag plis"

def solve():
    # Connect to the service
    io = remote('remote.infoseciitr.in', 4005)
    # io = process(['python3', 'chall.py'])
    
    # Receive banner
    io.recvuntil(b'one key at a time...')
    
    # Rotate keys 3 times to get 4 keys total
    for _ in range(3):
        io.sendlineafter(b'Your choice: ', b'1')
        io.recvuntil(b'Key rotated.')
    
    # Debug to get all keys and nonce
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
    print(f"Keys: {[k.hex() for k in keys]}")
    print(f"Nonce: {nonce_hex}")
    
    # Strategy: Create a ciphertext that decrypts differently with each key
    # The challenge uses: service.decrypt(ct, key)[16 * i:16 * (i+1)]
    # So with key[i], it takes bytes [16*i:16*(i+1)] from the decrypted plaintext
    
    # We need:
    # - With key[0]: bytes[0:16] should decrypt to "gib m" (+ padding)
    # - With key[1]: bytes[16:32] should decrypt to "e fl" (+ padding)
    # - With key[2]: bytes[32:48] should decrypt to "ag p" (+ padding)
    # - With key[3]: bytes[48:64] should decrypt to "lis" (+ padding)
    
    # Split the message into 4 chunks that don't end with spaces
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create a 64-byte plaintext where each 16-byte chunk contains the appropriate part
    plaintext = b""
    for part in parts:
        # Pad to 16 bytes with spaces (which will be stripped)
        plaintext += part.encode().ljust(16, b' ')
    
    print(f"Plaintext length: {len(plaintext)} bytes")
    print(f"Plaintext chunks:")
    for i in range(4):
        chunk = plaintext[16 * i:16 * (i+1)]
        print(f"  [{i}] bytes {16*i:2d}-{16*(i+1):2d}: {repr(chunk)} -> '{chunk.decode().strip()}'")
    
    # Now we need to encrypt this in a way that:
    # - Decrypting with key[0] and taking bytes[0:16] gives us the first chunk
    # - Decrypting with key[1] and taking bytes[16:32] gives us the second chunk
    # - etc.
    
    # The trick: We can only submit ONE ciphertext
    # But the service will decrypt it 4 times with 4 different keys
    # Each decryption with a different key will produce a different plaintext!
    
    # In AES-GCM-SIV, the ciphertext depends on both key and plaintext
    # We need to find a ciphertext C such that:
    # - decrypt(C, key[0])[0:16] = "gib m..."
    # - decrypt(C, key[1])[16:32] = "e fl..."
    # - decrypt(C, key[2])[32:48] = "ag p..."
    # - decrypt(C, key[3])[48:64] = "lis..."
    
    # This is actually impossible with standard AES-GCM-SIV!
    # A ciphertext can only decrypt to ONE specific plaintext with a given key.
    
    # Wait, let me re-read the code more carefully...
    # Actually, the service decrypts the SAME ciphertext with DIFFERENT keys
    # and takes different slices. This means we need the impossible:
    # One ciphertext that decrypts to different plaintexts with different keys.
    
    # Actually, this IS possible! Each key will decrypt to a different (likely garbage) plaintext
    # We need to find a ciphertext such that when decrypted with each key,
    # the specific 16-byte slice we need happens to be correct.
    
    # This is still extremely difficult because:
    # 1. We don't control the keys (they're random)
    # 2. AES-GCM-SIV will fail authentication with wrong keys
    
    # Wait, let me check the decrypt function...
    # It catches exceptions and returns None
    # But then the code checks: if not text or len(text) == 0 or text is None
    # So if decryption fails, it will exit.
    
    # Hmm, this seems impossible unless...
    # Let me think about the AAD (Additional Authenticated Data)
    # In the original it was self.aead = b"", in revenge it's self.aad = b""
    # Both are empty, so no difference there.
    
    # Actually, wait! Let me look at the exact error handling:
    # try:
    #     key = binascii.unhexlify(KEYS[i])
    #     ct = binascii.unhexlify(CIPHERTEXTS[i % len(CIPHERTEXTS)])
    #     text = service.decrypt(ct, key)[16 * i:16 * (i+1)].decode('utf-8').strip()
    #     if not text or len(text) == 0 or text is None:
    #         print("why so rude :(\n")
    #         exit(0)
    # except Exception:
    #     print("you have no honour!\n")
    #     exit(0)
    
    # If decrypt fails (returns None), then text = None[16*i:16*(i+1)] will raise TypeError
    # That gets caught and prints "you have no honour!"
    
    # So we NEED the ciphertext to decrypt successfully with all 4 keys...
    # But that's cryptographically impossible with AES-GCM-SIV!
    
    # Unless... there's something about the way they're using it?
    # Let me check if there's a way to forge a ciphertext...
    
    # Actually, I think I'm overcomplicating this. Let me try the simple approach:
    # Encrypt the full 64-byte plaintext with key[0] and see what happens
    
    print("\nAttempt 1: Encrypt with key[0]")
    ciphertext = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
    print(f"Ciphertext: {ciphertext.hex()}")
    
    # Test what happens when we decrypt with each key
    print("\nLocal test:")
    for i in range(4):
        key = keys[i]
        try:
            decrypted = AESGCMSIV(key).decrypt(nonce, ciphertext, b"")
            chunk = decrypted[16 * i:16 * (i+1)].decode('utf-8', errors='replace').strip()
            print(f"  Key[{i}] decrypt: bytes[{16*i}:{16*(i+1)}] = '{chunk}'")
        except Exception as e:
            print(f"  Key[{i}] decrypt: FAILED - {e}")
    
    # This will probably only work with key[0]...
    # Let me think of another approach
    
    print("\n" + "="*60)
    print("Hmm, standard approach won't work. Let me analyze the problem...")
    print("="*60)
    
    # The only way this could work is if there's a property of AES-GCM-SIV
    # that allows decryption with wrong keys to produce specific patterns...
    # Or if the keys have some special relationship...
    
    # Actually, let me try encrypting EACH chunk with its corresponding key!
    # Maybe we can construct a frankenstein ciphertext?
    
    print("\nAttempt 2: Create composite ciphertext")
    # This won't work either because AES-GCM-SIV includes authentication tag
    
    # Let me try one more thing: what if we submit multiple ciphertexts?
    # Oh wait, CIPHERTEXTS_LEN = 1, so we can only submit one.
    
    # And the code uses: CIPHERTEXTS[i % len(CIPHERTEXTS)]
    # So it always uses the same ciphertext
    
    # I think the key insight is that with different keys, the same ciphertext
    # will fail to decrypt (authentication error) for keys 1-3
    # But maybe there's a vulnerability in the error handling?
    
    # Actually, let me re-read line 96:
    # text = service.decrypt(ct, key)[16 * i:16 * (i+1)].decode('utf-8').strip()
    # If decrypt returns None, this will crash with TypeError (NoneType has no __getitem__)
    # Which gets caught and exits with "you have no honour!"
    
    # So we MUST have successful decryption with all 4 keys.
    
    # Wait! What if the keys are related? Let me check if there's a pattern...
    print(f"\nAnalyzing key relationship:")
    for i in range(len(keys)):
        print(f"Key[{i}]: {keys[i].hex()}")
    
    # They're random, so no obvious relationship...
    
    # Let me try submitting anyway and see what the actual error is
    io.sendlineafter(b'Your choice: ', b'3')
    io.sendlineafter(b'Enter ciphertext (hex): ', ciphertext.hex().encode())
    
    io.sendlineafter(b'Your choice: ', b'4')
    
    try:
        response = io.recvall(timeout=2).decode()
        print(f"\nServer response:\n{response}")
    except:
        print("Connection closed or timeout")
    
    io.close()

if __name__ == '__main__':
    solve()
