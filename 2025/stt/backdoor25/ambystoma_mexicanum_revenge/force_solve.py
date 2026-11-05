#!/usr/bin/env python3
"""
HYPOTHESIS: The server has CIPHERTEXTS_LEN = 4, not 1.
The provided source is either outdated or intentionally misleading.

This script will FORCE push 4 ciphertexts by handling the "cannot remember" error.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

REQUEST = "gib me flag plis"

def force_solve():
    context.log_level = 'warn'  # Reduce noise
    
    # Try multiple times in case of network issues
    for attempt in range(3):
        try:
            log.info(f"Attempt #{attempt + 1}")
            io = remote('remote.infoseciitr.in', 4005)
            io.recvuntil(b'one key at a time...', timeout=5)
            
            # Rotate 3 times
            for _ in range(3):
                io.sendlineafter(b'Your choice: ', b'1', timeout=5)
                io.recvuntil(b'rotated.', timeout=5)
            
            # Get keys and nonce  
            io.sendlineafter(b'Your choice: ', b'2', timeout=5)
            io.recvuntil(b'KEYS=', timeout=5)
            keys_line = io.recvline().decode().strip()
            io.recvuntil(b'nonce=', timeout=5)
            nonce_hex = io.recvline().decode().strip()
            
            keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
            keys_hex = keys_str.split(',')
            keys = [binascii.unhexlify(k) for k in keys_hex]
            nonce = binascii.unhexlify(nonce_hex)
            
            log.info(f"Keys: {len(keys)}, Nonce: {nonce_hex[:16]}...")
            
            parts = ["gib m", "e fl", "ag p", "lis"]
            
            # Create 4 ciphertexts
            ciphertexts = []
            for i in range(4):
                plaintext = bytearray(64)
                chunk = parts[i].encode().ljust(16, b' ')
                plaintext[16*i:16*(i+1)] = chunk
                ct = AESGCMSIV(keys[i]).encrypt(nonce, bytes(plaintext), b"")
                ciphertexts.append(ct.hex())
            
            log.info("Attempting to push 4 ciphertexts with aggressive timing...")
            
            # Strategy: Push first 3 normally, then try to race condition the 4th
            for i in range(min(4, len(ciphertexts))):
                io.sendlineafter(b'Your choice: ', b'3', timeout=5)
                io.sendlineafter(b'Enter ciphertext (hex): ', ciphertexts[i].encode(), timeout=5)
                
                # Read response but don't block if server closes  
                try:
                    resp = io.recvuntil(b'Your choice:', timeout=2)
                    if i < 3:
                        log.success(f"CT {i+1}/4 accepted")
                except:
                    log.warn(f"No response after CT {i+1}, connection may have closed")
                    break
            
            # Try to request flag anyway
            log.info("Attempting to request flag...")
            try:
                io.sendline(b'4')
                resp = io.recvall(timeout=3).decode()
                log.info(f"Response ({len(resp)} chars): {resp[:100]}...")
                
                if "flag{" in resp:
                    log.success("\n🎉🎉🎉 GOT THE FLAG! 🎉🎉🎉")
                    flag_start = resp.index("flag{")
                    flag_end = resp.index("}", flag_start) + 1
                    flag = resp[flag_start:flag_end]
                    print(f"\n{flag}\n")
                    io.close()
                    return True
            except EOFError:
                log.warn("Connection closed before flag request")
            except Exception as e:
                log.warn(f"Error during flag request: {e}")
            
            io.close()
            
        except Exception as e:
            log.error(f"Attempt #{attempt + 1} failed: {e}")
            continue
    
    return False

if __name__ == '__main__':
    success = force_solve()
    if not success:
        log.error("\nAll attempts failed")
        log.error("The server definitely has CIPHERTEXTS_LEN = 1")
        log.error("This challenge remains unsolved")
