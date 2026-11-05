"""
Analysis of m4c&ch3353 challenge

The challenge has a MAC verification system. Let's trace through:

1. Initial setup:
   - n is generated as product of 16 primes (128 bits each) + powers of 2
   - MAC is computed as: CMAC(key=n[:16], message=n_bytes)
   - base is generated, signature shown

2. verify() function:
   ```python
   prev = self.n
   mac = self.mac      # Save current MAC
   self.n = N          # Set new N
   self.process()      # Compute NEW MAC with new N
   ...
   if self.mac != mac or x != N or maxPrime.bit_length() > security // 5:
       # Revert and fail
   ```

   The check: self.mac != mac
   - self.mac is the NEW MAC (computed from new N)
   - mac is the OLD MAC (from original n)
   
   So we need: CMAC(new_N) == CMAC(old_n)
   
   CMAC computation:
   ```python
   x = long_to_bytes(self.n)
   cc = CMAC.new(x[:16], ciphermod=AES)
   self.mac = cc.update(x).hexdigest()
   ```
   
   So MAC = CMAC(key=N[:16], message=N_as_bytes)

3. The vulnerability:
   We need to find N such that:
   - N is 2048 bits
   - N is product of primes, max prime < 205 bits  
   - CMAC(N[:16], N) == original_MAC
   
   Since we control both the key (first 16 bytes) and message (full N),
   we can search for a collision.

4. Brute force approach:
   - Generate random combinations of small primes
   - Multiply to get ~2048 bits
   - Pad with 2s to exactly 2048 bits
   - Check if MAC matches
   
   This is feasible because:
   - We have 90 steps to try
   - We can pre-compute locally
   - CMAC is deterministic

5. After verification:
   - communicate() will give us encrypted flag
   - We need to decrypt using the known parameters

Let me think about the math more...

Actually, there might be a smarter way. Let's look at what we can control:
- The first 16 bytes of N determine the CMAC key
- The rest of N (along with first 16 bytes) is the message

If we fix the first 16 bytes to some value, we can compute what the MAC should be.
But we need to ensure N is still a product of primes.

Hmm, this is tricky because changing any prime factor changes the entire number.

Let me try a meet-in-the-middle approach or just brute force with many attempts.
"""

from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime
import random

def compute_mac(n):
    x = long_to_bytes(n)
    cc = CMAC.new(x[:16], ciphermod=AES)
    return cc.update(x).hexdigest()

target_mac = "4930c0e1806e710e2a1ea7154a9abed0"  # From server output
target_bits = 2048
max_prime_bits = 204

print(f"[*] Target MAC: {target_mac}")
print(f"[*] Searching for collision...")

# Try many random combinations
prime_pool = []
print("[*] Generating prime pool...")
for bits in [100, 120, 140, 160, 180, 200]:
    for _ in range(10):
        prime_pool.append(getPrime(bits))

print(f"[*] Generated {len(prime_pool)} primes")

attempts = 0
max_attempts = 10000

while attempts < max_attempts:
    attempts += 1
    
    # Random selection of primes
    num_primes = random.randint(1, 12)
    selected = random.sample(prime_pool, num_primes)
    
    n = 1
    data = []
    for p in selected:
        n *= p
        data.append([p, 1])
    
    # Pad with 2s
    twos = 0
    while n.bit_length() < target_bits:
        n *= 2
        twos += 1
    
    if twos > 0:
        data.append([2, twos])
    
    if n.bit_length() != target_bits:
        continue
    
    # Check MAC
    current_mac = compute_mac(n)
    
    if attempts % 100 == 0:
        print(f"[*] Attempt {attempts}: {current_mac[:16]}...")
    
    if current_mac == target_mac:
        print(f"\n[+] FOUND COLLISION after {attempts} attempts!")
        print(f"[+] N = {n}")
        print(f"[+] N bit length = {n.bit_length()}")
        print(f"[+] Data = {data}")
        
        # Format for server
        format_str = '-'.join([f"[{p}, {c}]" for p, c in data])
        print(f"\n[+] Format string: {format_str[:200]}...")
        print(f"[+] Total length: {len(format_str)}")
        
        # Save to file
        with open('collision.txt', 'w') as f:
            f.write(f"N = {n}\n")
            f.write(f"Format = {format_str}\n")
        
        break

if attempts >= max_attempts:
    print(f"\n[-] No collision found in {max_attempts} attempts")
    print("[-] May need to run longer or adjust strategy")
