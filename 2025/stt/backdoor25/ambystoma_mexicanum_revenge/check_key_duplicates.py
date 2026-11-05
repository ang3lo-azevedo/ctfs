#!/usr/bin/env python3
from pwn import *

# Test if rotating keys might give duplicate keys
# (Maybe RNG is seeded or broken?)

io = remote('remote.infoseciitr.in', 4005)
io.recvuntil(b'one key at a time...')

# Rotate a bunch of times and collect keys
keys_sets = []
for iteration in range(3):
    # Get current keys
    io.sendlineafter(b'Your choice: ', b'2')
    io.recvuntil(b'KEYS=')
    keys_line = io.recvline().decode().strip()
    io.recvuntil(b'nonce=')
    io.recvline()
    
    print(f"\nIteration {iteration}: {keys_line}")
    keys_sets.append(keys_line)
    
    # Rotate
    io.sendlineafter(b'Your choice: ', b'1')
    io.recvuntil(b'rotated.')

# Get final state
io.sendlineafter(b'Your choice: ', b'2')
io.recvuntil(b'KEYS=')
keys_line = io.recvline().decode().strip()
print(f"\nFinal: {keys_line}")

# Parse and check for duplicates
keys_str = keys_line.replace('[', '').replace(']', '').replace("'", "").replace(" ", "")
keys = keys_str.split(',')
print(f"\nAll keys: {keys}")
print(f"Unique keys: {set(keys)}")
print(f"Duplicates? {len(keys) != len(set(keys))}")

io.close()
