"""
Smarter approach to finding MAC collision

Key insight: CMAC is computed as:
    cc = CMAC.new(N_bytes[:16], ciphermod=AES)
    mac = cc.update(N_bytes).hexdigest()

So the MAC depends on:
1. The key: first 16 bytes of N
2. The message: all bytes of N

For 2048-bit N, we have 256 bytes total.

If we want to find a collision, we need to think about the structure of N.

N must be a product of primes where max prime < 205 bits.

One approach: Use a fixed set of small primes for the first portion (to control first 16 bytes),
then vary the larger primes to search for collision.

Actually, let's think about this differently:
- We can use many small primes (like 2) to pad
- We can use a few large primes to vary the value
- The first 16 bytes (128 bits) are determined by the lower-order bits of N

Wait, that's not quite right. In big-endian byte representation:
- First bytes are the MOST significant
- Last bytes are the LEAST significant

So if N = p1 * p2 * ... * pk * 2^m, the first bytes depend on the product structure.

Let me try a different strategy:
1. Fix most of the primes
2. Vary one or two primes to search for collision
3. This gives us more controlled search space
"""

from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime, isPrime
import itertools

def compute_mac(n):
    x = long_to_bytes(n)
    cc = CMAC.new(x[:16], ciphermod=AES)
    return cc.update(x).hexdigest()

target_mac = "4930c0e1806e710e2a1ea7154a9abed0"
target_bits = 2048
max_prime_bits = 204

print(f"[*] Target MAC: {target_mac}")

# Strategy: Build N with a fixed base and variable component
# N = base * variable * 2^padding
# Where base is product of several primes, variable is one prime we iterate

print("[*] Generating base primes...")

# Generate a set of medium-sized primes for the base
base_primes = []
base = 1
for bits in [180, 170, 160, 150, 140]:
    p = getPrime(bits)
    base_primes.append(p)
    base *= p
    print(f"    Added {bits}-bit prime, base is now {base.bit_length()} bits")

print(f"[*] Base product: {base.bit_length()} bits")
print(f"[*] Need to add: {target_bits - base.bit_length()} more bits")

# Now we'll iterate through different combinations for the remaining bits
remaining_bits = target_bits - base.bit_length()

print(f"\n[*] Searching for collision by varying {remaining_bits}-bit component...")

attempts = 0
for attempt in range(50000):
    attempts += 1
    
    # Generate one or two more primes to fill the remaining space
    variable_primes = []
    variable_product = 1
    
    # Try different combinations
    if remaining_bits > 400:
        # Use 2 large primes
        p1_bits = remaining_bits // 2
        p2_bits = remaining_bits - p1_bits - 50  # Leave room for padding
        
        if p1_bits <= max_prime_bits and p2_bits <= max_prime_bits:
            p1 = getPrime(p1_bits)
            p2 = getPrime(p2_bits)
            variable_primes = [p1, p2]
            variable_product = p1 * p2
    else:
        # Use 1 large prime
        p_bits = min(remaining_bits - 20, max_prime_bits)
        p = getPrime(p_bits)
        variable_primes = [p]
        variable_product = p
    
    # Compute N
    n = base * variable_product
    
    # Pad with 2s
    twos = 0
    while n.bit_length() < target_bits:
        n *= 2
        twos += 1
    
    if n.bit_length() != target_bits:
        continue
    
    # Build data array
    data = [[p, 1] for p in base_primes + variable_primes]
    if twos > 0:
        data.append([2, twos])
    
    # Check MAC
    current_mac = compute_mac(n)
    
    if attempts % 100 == 0:
        print(f"[*] Attempt {attempts}: MAC = {current_mac[:16]}...")
    
    if current_mac == target_mac:
        print(f"\n[+] COLLISION FOUND after {attempts} attempts!")
        print(f"[+] N = {n}")
        print(f"[+] N bit length = {n.bit_length()}")
        print(f"[+] Data: {len(data)} terms")
        
        # Verify it's correct
        check = 1
        for p, count in data:
            check *= pow(p, count)
        assert check == n, "Product doesn't match!"
        assert n.bit_length() == target_bits, "Wrong bit length!"
        assert compute_mac(n) == target_mac, "MAC doesn't match!"
        
        print("[+] All checks passed!")
        
        # Format for server
        format_str = '-'.join([f"[{p}, {c}]" for p, c in data])
        
        # Save to file
        with open('collision.txt', 'w') as f:
            f.write(f"{n}\n")
            f.write(f"{format_str}\n")
        
        print(f"\n[+] Saved to collision.txt")
        print(f"[+] Format string length: {len(format_str)}")
        
        break

if attempts >= 50000:
    print(f"\n[-] No collision found in {attempts} attempts")
