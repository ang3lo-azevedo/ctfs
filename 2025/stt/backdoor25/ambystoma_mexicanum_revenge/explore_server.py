#!/usr/bin/env python3
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
from pwn import *
import binascii

io = remote('remote.infoseciitr.in', 4005)
io.recvuntil(b'one key at a time...')

# First, let's check what happens if we DON'T rotate at all
print("Testing with NO key rotation:")
io.sendlineafter(b'Your choice: ', b'2')
debug_output = io.recvuntil(b'Your choice: ').decode()
print(debug_output)

# Now let's rotate once and check
print("\nTesting after 1 rotation:")
io.sendlineafter(b'Your choice: ', b'1')
io.recvuntil(b'rotated.')
io.sendlineafter(b'Your choice: ', b'2')
debug_output = io.recvuntil(b'Your choice: ').decode()
print(debug_output)

# Check if we can push without rotating back to 1 key
print("\nNow let's see what happens with 2 keys...")

# Extract keys and nonce
io.sendlineafter(b'Your choice: ', b'2')
io.recvuntil(b'KEYS=')
keys_line = io.recvline().decode().strip()
io.recvuntil(b'nonce=')
nonce_hex = io.recvline().decode().strip()

keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
keys_hex = keys_str.split(',')
keys = [binascii.unhexlify(k) for k in keys_hex]
nonce = binascii.unhexlify(nonce_hex)

print(f"\nWe have {len(keys)} keys")
print(f"Nonce: {nonce_hex}")

# Now, what if the bug is that with only 2 keys, the modulo behavior is different?
# Let's try: with 2 keys and 1 ciphertext
# i=0: key[0], ct[0]
# i=1: key[1], ct[0]  
# i=2: key[2] -> IndexError!
# i=3: key[3] -> IndexError!

# So that won't work either...

# Let me try one more thing: what if we can somehow make the ciphertext list have multiple elements?
# By exploiting the input parsing?

print("\nTrying to push a ciphertext with special formatting:")
# What if we send something like: "aabbcc,ddeeff" hoping it gets split?
io.sendlineafter(b'Your choice: ', b'3')
io.sendlineafter(b'Enter ciphertext (hex): ', b'0011223344556677')

io.sendlineafter(b'Your choice: ', b'2')
debug_output = io.recvuntil(b'Your choice: ').decode()
print("After pushing ciphertext:")
print(debug_output)

io.close()
