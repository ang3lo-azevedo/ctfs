from pwn import *

context.log_level = 'debug'

io = remote('remote.infoseciitr.in', 4001)

# Get initial values
io.recvuntil(b'My m4c&ch3353: ')
mac = io.recvline().strip().decode()
print(f"\n[+] MAC: {mac}")

io.recvuntil(b'My signature:  ')
signature = int(io.recvline().strip().decode())
print(f"[+] Signature: {signature}")

print(f"[+] Signature bit length: {signature.bit_length()}")

# Let's try to use the power_tower function (option 4) to get information
# But wait, option 4 is "Quit", not power_tower

# Let me check what functions are available
print("\n[*] Available options:")
print("1: Communicate (needs verification)")
print("2: Verify")
print("3: Obfuscating (leaks key information)")
print("4: Quit")

# Let's try calling power_tower through option...
# Actually, looking at the code, power_tower method exists but isn't exposed in the menu!

# Let's try a completely different approach:
# Use obfuscateSmall to leak the 96 individual prime keys
# Then see if we can use that information somehow

print("\n[*] Attempting to leak key structure...")

# Try some edge cases with obfuscateSmall
test_values = [
    0,
    1,
    2,
    (1 << 96) - 1,  # All 96 bits set
    1 << 96,  # Just above the mask
    (1 << 96) + 1,
]

for val in test_values:
    io.recvuntil(b'Choose: ')
    io.sendline(b'3')
    io.recvuntil(b'Enter your message : ')
    io.sendline(str(val).encode())
    io.recvuntil(b'Here is your obfuscated message :  ')
    result = int(io.recvline().strip())
    print(f"obfuscateSmall({val}) = {result}")

io.interactive()
