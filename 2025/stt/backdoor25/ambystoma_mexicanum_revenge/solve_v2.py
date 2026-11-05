#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

# Target message: "gib me flag plis"
REQUEST = "gib me flag plis"

def solve():
    # Connect to the service
    io = remote('remote.infoseciitr.in', 4005)
    
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
    print(f"Nonce: {nonce_hex}")
    
    # New approach: What if we encrypt different plaintexts with each key?
    # Each plaintext should have the right chunk at the right position
    
    # For key[0], we need bytes[0:16] = "gib m"
    # For key[1], we need bytes[16:32] = "e fl"  
    # For key[2], we need bytes[32:48] = "ag p"
    # For key[3], we need bytes[48:64] = "lis"
    
    # So let's create a plaintext for each key where:
    # - Plaintext for key[i] has the correct chunk at position [16*i:16*(i+1)]
    # - The rest can be anything (we just need to avoid crashes)
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create 4 different plaintexts, each with the appropriate chunk in the right place
    plaintexts = []
    for i in range(4):
        pt = bytearray(64)  # 64 bytes total
        # Place the correct part at position [16*i:16*(i+1)]
        chunk = parts[i].encode().ljust(16, b' ')
        pt[16*i:16*(i+1)] = chunk
        plaintexts.append(bytes(pt))
    
    # Now encrypt each plaintext with its corresponding key
    ciphertexts = []
    for i in range(4):
        ct = AESGCMSIV(keys[i]).encrypt(nonce, plaintexts[i], b"")
        ciphertexts.append(ct)
        print(f"Ciphertext[{i}]: {ct.hex()[:40]}...")
    
    # Now the question is: can we combine these ciphertexts somehow?
    # Or do we need a different approach?
    
    # Actually, looking at the code again:
    # ct = binascii.unhexlify(CIPHERTEXTS[i % len(CIPHERTEXTS)])
    # It uses the SAME ciphertext for all iterations (i % len = i % 1 = 0)
    
    # So we can only submit ONE ciphertext, and it must work with all keys...
    
    # Hmm, what if we try to XOR the ciphertexts? No, that won't work with AEAD.
    
    # Let me think about the actual crypto here:
    # AES-GCM-SIV = AES-CTR encryption + GMAC authentication
    # The key is used for both encryption and authentication
    # Different keys = different auth tags = decryption will fail
    
    # Unless... what if there's a vulnerability in the implementation?
    # Or what if we can find a ciphertext that passes authentication for multiple keys?
    
    # Actually, I wonder if the challenge expects us to brute force something?
    # Or maybe there's a mathematical relationship we can exploit?
    
    # Let me try a different approach: what if we don't encrypt properly?
    # What if we just create a raw ciphertext and see what happens?
    
    # Actually, let me re-read the challenge description:
    # "The axolotls are not what they seem, they are back now, with a revenge."
    # "not what they seem" - maybe there's a trick in how the crypto is implemented?
    
    # Let me check if there's something special about the slicing logic...
    # text = service.decrypt(ct, key)[16 * i:16 * (i+1)]
    # 
    # Wait! What if the decrypted plaintext is shorter than expected?
    # If decrypt(ct, key[1]) produces a plaintext shorter than 32 bytes,
    # then [16:32] might go out of bounds... but Python slicing doesn't error on that,
    # it just returns less data.
    
    # So maybe we can encrypt shorter plaintexts?
    # Let's try encrypting just the minimum needed for each key
    
    print("\n" + "="*60)
    print("Trying approach with variable-length plaintexts")
    print("="*60)
    
    # For key[i], we need at least 16*(i+1) bytes of plaintext
    # So:
    # - key[0]: needs at least 16 bytes (we want bytes[0:16])
    # - key[1]: needs at least 32 bytes (we want bytes[16:32])
    # - key[2]: needs at least 48 bytes (we want bytes[32:48])
    # - key[3]: needs at least 64 bytes (we want bytes[48:64])
    
    # But we can only use ONE ciphertext...
    # So it must decrypt to different plaintexts with each key
    
    # I think the solution requires finding a cryptographic collision or weakness
    # which is beyond the scope of a typical CTF challenge...
    
    # Unless... let me check if maybe we misunderstood the code?
    # Let me re-read it very carefully...
    
    io.close()
    return

if __name__ == '__main__':
    solve()
