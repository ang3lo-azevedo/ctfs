#!/usr/bin/env python3
from pwn import *
import json
import base64

# Connect to the server
io = remote('challs.glacierctf.com', 13387)

# Receive the welcome message
io.recvuntil(b'Exit\n')

# Step 1: Get a token
io.sendline(b'1')
io.recvuntil(b'name?\n')
io.sendline(b'test')

io.recvuntil(b'Here is your token: ')
token_str = io.recvline().strip().decode()
print(f"[+] Received token: {token_str}")

token = json.loads(token_str)
iv = base64.b64decode(token['iv'])
ct = base64.b64decode(token['ct'])

print(f"[+] Original IV: {iv.hex()}")
print(f"[+] Ciphertext: {ct.hex()}")

# The plaintext is: "admin=0;name=test"
# We want to flip the bit at position 6 to change '0' to '1'
# In CBC mode, flipping bit i in IV flips bit i in the first plaintext block

# '0' = 0x30, '1' = 0x31
# We need to XOR position 6 of IV with 0x30 XOR 0x31 = 0x01

iv_modified = bytearray(iv)
iv_modified[6] ^= 0x01  # Flip the bit to change '0' to '1'

print(f"[+] Modified IV: {bytes(iv_modified).hex()}")

# Create the modified token
modified_token = {
    'iv': base64.b64encode(bytes(iv_modified)).decode(),
    'ct': base64.b64encode(ct).decode()
}

modified_token_str = json.dumps(modified_token)
print(f"[+] Modified token: {modified_token_str}")

# Step 2: Redeem the modified token
io.recvuntil(b'Exit\n')
io.sendline(b'2')
io.recvuntil(b'token?\n')
io.sendline(modified_token_str.encode())

# Get the flag
response = io.recvall(timeout=2).decode()
print(f"\n[+] Response:\n{response}")

io.close()
