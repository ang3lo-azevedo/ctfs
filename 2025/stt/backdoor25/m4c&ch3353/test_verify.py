from pwn import *
from Crypto.Util.number import getPrime

context.log_level = 'info'

io = remote('remote.infoseciitr.in', 4001)

# Get initial values
io.recvuntil(b'My m4c&ch3353: ')
mac = io.recvline().strip().decode()
log.info(f"MAC: {mac}")

io.recvuntil(b'My signature:  ')
signature = int(io.recvline().strip().decode())
log.info(f"Signature: {signature}")

# Try submitting a simple valid N
log.info("Attempting verification with a simple N...")

# Build a simple 2048-bit N
primes = []
n = 1
for bits in [200, 200, 200, 200, 200, 200, 200, 180]:
    p = getPrime(bits)
    primes.append((p, 1))
    n *= p

log.info(f"N so far: {n.bit_length()} bits")

# Pad with 2s
twos = 0
while n.bit_length() < 2048:
    n *= 2
    twos += 1

if twos > 0:
    primes.append((2, twos))

log.info(f"Final N: {n.bit_length()} bits")
log.info(f"Number of prime factors: {len(primes)}")

# Send verification request
io.recvuntil(b'Choose: ')
io.sendline(b'2')
io.recvuntil(b'Give me the MY modulus : ')
io.sendline(str(n).encode())

io.recvuntil(b'Enter prime factorization')
format_str = '-'.join([f"[{p}, {c}]" for p, c in primes])
log.info(f"Sending format string (length: {len(format_str)})...")
io.sendline(format_str.encode())

# See what response we get
import time
time.sleep(1)
response = io.recvline().decode()
print("\n" + "="*60)
print("SERVER RESPONSE:")
print("="*60)
print(response)
print("="*60)
    
# Check if there's more output
try:
    io.recvuntil(b'Choose: ')
    print("Got menu prompt - verification completed!")
except:
    print("No menu prompt")
    
io.close()
