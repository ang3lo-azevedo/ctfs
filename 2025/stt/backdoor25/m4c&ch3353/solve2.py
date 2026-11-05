from pwn import *
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime
import math

context.log_level = 'info'

# Connect to remote
io = remote('remote.infoseciitr.in', 4001)

# Receive initial values
io.recvuntil(b'My m4c&ch3353: ')
mac = io.recvline().strip().decode()
log.info(f"MAC: {mac}")

io.recvuntil(b'My signature:  ')
signature = int(io.recvline().strip().decode())
log.info(f"Signature: {signature}")

"""
Analysis of the vulnerability:

The verify() function checks:
1. N has 2048 bits
2. All factors in data are prime
3. self.mac == mac (but mac is the OLD mac before changing self.n)
4. product of primes == N
5. max prime < 205 bits

The bug: After computing self.process() with new N, it compares self.mac with the OLD mac variable!
This means ANY N will pass as long as the old MAC equals itself (which it always does!)

Wait, let me re-read... 

```python
prev = self.n
mac = self.mac  # Save old mac
self.n = N
self.process()  # Compute NEW mac with NEW N
...
if self.mac != mac or x != N or maxPrime.bit_length() > self.security // 5:
    # Compare NEW mac with OLD mac
```

So we need NEW mac to equal OLD mac. This is the MAC collision challenge.

But wait - there's another way to think about this:
The MAC is computed as: CMAC with key = n[:16], message = entire n

If we construct N such that:
1. N[:16] == original_n[:16] (same key)
2. CMAC(N[:16], N) == CMAC(original_n[:16], original_n)

Actually, even simpler: if N[:16] == original_n[:16], and the MACs happen to collide, we win!

But we don't know original_n. Can we deduce it?

Looking at the generator:
- It uses 16 primes of 128 bits each (2048/128 = 16)
- Plus powers of 2 to pad to exactly 2048 bits

We can try to construct OUR OWN N that:
1. Uses small primes (< 205 bits)
2. Results in a MAC that matches the given one

Since we control the first 16 bytes and the rest, we can brute force!
"""

def compute_mac(n_bytes):
    """Compute CMAC of n_bytes using first 16 bytes as key"""
    cc = CMAC.new(n_bytes[:16], ciphermod=AES)
    return cc.update(n_bytes).hexdigest()

log.info("Attempting to brute force MAC collision...")

# Strategy: Try different combinations of small primes
# The first 16 bytes determine the key, and the full bytes determine the MAC
# We need to find a combination that produces the target MAC

from itertools import combinations_with_replacement

target_bits = 2048
max_prime_bits = 204

# Generate a pool of small primes
log.info("Generating prime pool...")
prime_pool = []
for bits in range(100, max_prime_bits + 1, 10):
    for _ in range(3):
        prime_pool.append(getPrime(bits))

log.info(f"Generated {len(prime_pool)} primes")

# Now try combinations
found = False
attempt = 0

# Try simpler approach: use power of 2s and a few primes
for num_primes in range(1, 15):
    if found:
        break
    
    log.info(f"Trying with {num_primes} primes...")
    
    for _ in range(20):  # Try 20 random combinations
        attempt += 1
        
        # Pick random primes
        import random
        primes = random.sample(prime_pool, min(num_primes, len(prime_pool)))
        
        n = 1
        data = []
        for p in primes:
            n *= p
            data.append([p, 1])
        
        # Pad with 2s
        twos_count = 0
        while n.bit_length() < target_bits:
            n *= 2
            twos_count += 1
        
        if twos_count > 0:
            data.append([2, twos_count])
        
        # Check bit length
        if n.bit_length() != target_bits:
            continue
        
        # Check MAC
        n_bytes = long_to_bytes(n)
        current_mac = compute_mac(n_bytes)
        
        if attempt % 50 == 0:
            log.info(f"Attempt {attempt}, current MAC: {current_mac[:16]}...")
        
        if current_mac == mac:
            log.success(f"Found collision after {attempt} attempts!")
            log.success(f"N: {n}")
            log.success(f"Data: {data}")
            
            # Send verification
            io.recvuntil(b'Choose: ')
            io.sendline(b'2')
            io.recvuntil(b'Give me the MY modulus : ')
            io.sendline(str(n).encode())
            io.recvuntil(b'Enter prime factorization')
            
            # Format: [prime1, count1]-[prime2, count2]-...
            format_str = '-'.join([f"[{p}, {c}]" for p, c in data])
            io.sendline(format_str.encode())
            
            print(io.recvall(timeout=2).decode())
            
            found = True
            break

if not found:
    log.error("Could not find MAC collision in reasonable time")
    log.info("Switching to interactive mode to debug...")
    io.interactive()
else:
    # Now we're verified, call communicate to get flag
    io.sendline(b'1')
    io.interactive()
