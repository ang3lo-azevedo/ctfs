#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV  
from pwn import *
import binascii

# Maybe there's a trick where we're supposed to use the SAME nonce/key combination?
# Or some other aspect of the protocol?

# Let me just try manually connecting and see what we can discover
io = remote('remote.infoseciitr.in', 4005)
print(io.recvuntil(b'Your choice: ').decode())

#Let me try just requesting the flag with the default state
io.sendline(b'4')
print(io.recvall(timeout=1).decode())
io.close()
