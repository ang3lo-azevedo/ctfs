from pwn import *
from Crypto.Util.number import getPrime
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes

context.log_level = 'warn'

# Connect multiple times to see if MAC changes
macs = []
signatures = []

for i in range(5):
    io = remote('remote.infoseciitr.in', 4001)
    io.recvuntil(b'My m4c&ch3353: ')
    mac = io.recvline().strip().decode()
    io.recvuntil(b'My signature:  ')
    sig = int(io.recvline().strip().decode())
    
    macs.append(mac)
    signatures.append(sig)
    
    print(f"Connection {i+1}:")
    print(f"  MAC: {mac}")
    print(f"  Sig (first 50 digits): {str(sig)[:50]}...")
    print(f"  Sig bit length: {sig.bit_length()}")
    
    io.close()

print("\n" + "="*60)
if len(set(macs)) == 1:
    print("ALL MACS ARE IDENTICAL!")
    print("This means the server uses the same n every time!")
    print(f"MAC: {macs[0]}")
else:
    print(f"MACs are different ({len(set(macs))} unique values)")

if len(set(signatures)) == 1:
    print("ALL SIGNATURES ARE IDENTICAL!")
else:
    print(f"Signatures are different ({len(set(signatures))} unique values)")
