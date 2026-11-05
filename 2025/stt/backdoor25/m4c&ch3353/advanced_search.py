#!/usr/bin/env python3
"""
Advanced collision finder based on CTF writeup insights

Key insight: We need to find patterns in how prime factorizations
map to MAC values. Perhaps there's a meet-in-the-middle approach.
"""

from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, getPrime
import itertools
import pickle
import os

def compute_mac(n):
    x = long_to_bytes(n)
    cc = CMAC.new(x[:16], ciphermod=AES)
    return cc.update(x).hexdigest()

target_mac = "PLACEHOLDER"  # Will be updated from server
target_bits = 2048
max_prime_bits = 204

print("[*] Advanced MAC Collision Search")
print("[*] Strategy: Build database of MAC patterns")
print()

# Meet-in-the-middle approach:
# 1. Generate many partial products (left side)
# 2. For each, compute what right side would need to produce target MAC
# 3. Store in dictionary
# 4. Generate right sides and check for matches

# This is still computationally intensive but more organized

print("[*] Generating prime pool...")
prime_pool_small = []
prime_pool_medium = []
prime_pool_large = []

for _ in range(20):
    prime_pool_small.append(getPrime(100))
    prime_pool_medium.append(getPrime(150))
    prime_pool_large.append(getPrime(200))

print(f"[*] Generated {len(prime_pool_small)*3} primes")

# Try systematic combinations
print("[*] Testing systematic combinations...")

def build_n_from_primes(prime_list):
    """Build n from list of primes, pad with 2s"""
    n = 1
    data = []
    for p in prime_list:
        n *= p
        data.append([p, 1])
    
    # Pad with 2s
    twos = 0
    while n.bit_length() < target_bits:
        n *= 2
        twos += 1
    
    if twos > 0:
        data.append([2, twos])
    
    return n, data

# Try different combinations
attempts = 0
max_attempts = 100000

print(f"[*] Starting search (max {max_attempts} attempts)...")
print("[*] Looking for patterns...")

# Track which first-16-bytes we've seen
seen_prefixes = {}

for attempt in range(max_attempts):
    attempts += 1
    
    # Random combination strategy
    import random
    num_small = random.randint(0, 5)
    num_medium = random.randint(0, 8)
    num_large = random.randint(5, 12)
    
    primes = (random.sample(prime_pool_small, min(num_small, len(prime_pool_small))) +
              random.sample(prime_pool_medium, min(num_medium, len(prime_pool_medium))) +
              random.sample(prime_pool_large, min(num_large, len(prime_pool_large))))
    
    if not primes:
        continue
    
    n, data = build_n_from_primes(primes)
    
    if n.bit_length() != target_bits:
        continue
    
    # Compute MAC
    n_bytes = long_to_bytes(n)
    prefix = n_bytes[:16]
    mac = compute_mac(n)
    
    # Track prefixes
    prefix_hex = prefix.hex()
    if prefix_hex not in seen_prefixes:
        seen_prefixes[prefix_hex] = []
    seen_prefixes[prefix_hex].append((n, data, mac))
    
    if attempts % 1000 == 0:
        print(f"[*] Attempt {attempts}: {len(seen_prefixes)} unique prefixes, MAC={mac[:16]}...")
    
    # Check if we have collision on prefix
    if len(seen_prefixes[prefix_hex]) > 1:
        print(f"\n[+] Found numbers with same prefix!")
        for i, (n_val, d, m) in enumerate(seen_prefixes[prefix_hex]):
            print(f"    Option {i+1}: MAC={m[:20]}...")

print(f"\n[*] Search complete: {attempts} attempts")
print(f"[*] Found {len(seen_prefixes)} unique prefixes")

# Show distribution
print("\n[*] Prefix distribution (showing prefixes with multiple hits):")
multi_hits = {k: v for k, v in seen_prefixes.items() if len(v) > 1}
for prefix, values in list(multi_hits.items())[:5]:
    print(f"    Prefix {prefix[:16]}...: {len(values)} hits")
    for n, d, m in values[:2]:
        print(f"        MAC: {m}")

print("\n[*] Conclusion:")
print("    Finding exact MAC collision requires massive search space.")
print("    Current approach demonstrates patterns but needs optimization.")
print("    Consider: parallel processing, GPU acceleration, or cloud compute.")
