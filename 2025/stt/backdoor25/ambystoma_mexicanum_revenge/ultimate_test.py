#!/usr/bin/env python3
"""
Ultimate test: Definitively determine CIPHERTEXTS_LEN on the server.

If it's 4, we can solve this. If it's 1, the challenge appears impossible.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

def ultimate_test():
    io = remote('remote.infoseciitr.in', 4005)
    io.recvuntil(b'one key at a time...')
    
    # Rotate 3 times to get 4 keys
    print("Getting 4 keys...")
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
    
    print(f"Keys: {len(keys)}")
    print(f"Nonce: {nonce_hex}\n")
    
    parts = ["gib m", "e fl", "ag p", "lis"]
    
    # Create 4 distinct ciphertexts
    print("Creating 4 ciphertexts...")
    ciphertexts = []
    for i in range(4):
        plaintext = bytearray(64)
        chunk = parts[i].encode().ljust(16, b' ')
        plaintext[16*i:16*(i+1)] = chunk
        ct = AESGCMSIV(keys[i]).encrypt(nonce, bytes(plaintext), b"")
        ciphertexts.append(ct.hex())
        print(f"  CT[{i}]: {len(ct)} bytes encrypted")
    
    # Try pushing 4 CTs one by one
    print("\nPushing ciphertexts to server...")
    cts_pushed = 0
    
    for i in range(4):
        print(f"\n  Pushing CT #{i+1}...")
        io.sendlineafter(b'Your choice: ', b'3')
        io.sendlineafter(b'Enter ciphertext (hex): ', ciphertexts[i].encode())
        
        # Try to read response
        try:
            resp = io.recv(timeout=2)
            if b'cannot remember' in resp:
                print(f"    ❌ Server rejected! CIPHERTEXTS_LEN = {i}")
                print(f"    Response: {resp.decode()}")
                io.close()
                return i
            elif b'Your choice:' in resp:
                print(f"    ✅ Accepted!")
                cts_pushed += 1
            else:
                print(f"    ? Unexpected response: {resp[:50]}")
        except:
            print(f"    ❌ Connection closed or timeout")
            io.close()
            return i
    
    # If we got here, all 4 were accepted!
    print(f"\n✅✅✅ ALL 4 CIPHERTEXTS ACCEPTED! ✅✅✅")
    print(f"CIPHERTEXTS_LEN >= 4 on the server!")
    
    # Verify with debug
    print("\nVerifying with debug...")
    io.sendlineafter(b'Your choice: ', b'2')
    debug_output = io.recvuntil(b'Your choice:').decode()
    print(debug_output)
    
    # NOW REQUEST THE FLAG!
    print("\n🎯 REQUESTING FLAG...")
    io.sendline(b'4')
    
    response = io.recvall(timeout=3).decode()
    print(f"\nServer response:\n{response}")
    
    if "flag{" in response:
        print("\n" + "="*60)
        print("🎉🎉🎉 FLAG CAPTURED! 🎉🎉🎉")
        print("="*60)
        flag_start = response.index("flag{")
        flag_end = response.index("}", flag_start) + 1
        flag = response[flag_start:flag_end]
        print(f"\nFLAG: {flag}\n")
        print("="*60)
        return True
    else:
        print("\n❌ No flag in response")
    
    io.close()
    return False

if __name__ == '__main__':
    result = ultimate_test()
    if result == 1:
        print("\n" + "="*60)
        print("CONFIRMED: Server has CIPHERTEXTS_LEN = 1")
        print("This challenge is UNSOLVABLE with standard cryptography")
        print("="*60)
    elif result is True:
        print("\nChallenge SOLVED!")
    else:
        print(f"\nTest inconclusive (result: {result})")
