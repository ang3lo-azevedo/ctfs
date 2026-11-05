#!/usr/bin/env python3
"""
Test with corrected understanding of coefficient order
"""

MOD = 10**9 + 7

# Load numbers
with open('numbers.txt', 'r') as f:
    numbers = list(map(int, f.read().strip().split(',')))

print(f"[+] Loaded {len(numbers)} numbers")

def get_hash(num, coeff_arr):
    """
    Server iterates: for i in range(len(coeff_arr)):
        hash = (hash + mult * coeff_arr[len(coeff_arr)-1-i]) % mod
        mult = (mult * num) % mod
    
    So for coeffs [a, b, c]:
    i=0: hash = 0 + 1 * coeffs[2] = c
    i=1: hash = c + num * coeffs[1] = c + num*b
    i=2: hash = (c + num*b) + num^2 * coeffs[0] = c + b*num + a*num^2
    
    So coeffs = [a, b, c] gives polynomial: c + b*x + a*x^2 (REVERSED!)
    """
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % MOD
        mult = (mult * num) % MOD
    return hash_val

# Test constant f(x) = 5
print("\n[*] Testing f(x) = 5:")
coeffs = [5]  # This is the constant term
hashes = [get_hash(num, coeffs) for num in numbers]
print(f"    All hash to: {set(hashes)}")
print(f"    ✓ Correct: constant polynomial")

# Test linear f(x) = 0 + 1*x = x
print("\n[*] Testing f(x) = x:")
coeffs = [1, 0]  # [a, b] gives b + a*x, so [1, 0] gives 0 + 1*x = x
hashes = [get_hash(num, coeffs) for num in numbers[:5]]
print(f"    First 5 numbers: {numbers[:5]}")
print(f"    Their hashes: {hashes}")
print(f"    Expected (num % MOD): {[n % MOD for n in numbers[:5]]}")

# Ah! So [1, 0] gives us f(x) = x
# Let's test [0, 1] which should give us f(x) = 1
coeffs = [0, 1]
hashes = [get_hash(num, coeffs) for num in numbers[:5]]
print(f"\n[*] Testing coeffs [0, 1]:")
print(f"    Hashes: {hashes}")

# So to get balanced distribution, we need creative coefficients
print("\n[*] Searching for working polynomial...")

import random
random.seed(42)

for attempt in range(20000):
    # Try different patterns
    if attempt < 5000:
        # Small equal coefficients
        length = random.randint(50, 400)
        val = random.randint(1, 50)
        coeffs = [val] * length
    elif attempt < 10000:
        # Random small coefficients
        length = random.randint(50, 400)
        coeffs = [random.randint(0, 20) for _ in range(length)]
    elif attempt < 15000:
        # Larger random coefficients
        length = random.randint(100, 500)
        coeffs = [random.randint(0, 100) for _ in range(length)]
    else:
        # Very high degree with tiny coefficients
        length = random.randint(400, 800)
        coeffs = [random.randint(0, 5) for _ in range(length)]
    
    hashes = [get_hash(num, coeffs) for num in numbers]
    
    if all(h < 256 for h in hashes):
        # Check distribution
        slot_counts = [0] * 256
        for h in hashes:
            slot_counts[h] += 1
        
        non_empty = [c for c in slot_counts if c > 0]
        if len(non_empty) > 0:
            diff = max(non_empty) - min(non_empty)
            max_per_slot = (len(numbers) + 256 - 1) // 256
            
            if diff < 2 and all(c <= max_per_slot for c in slot_counts):
                print(f"\n[+] ✓ FOUND WORKING POLYNOMIAL!")
                print(f"    Length: {length}")
                print(f"    Pattern: {coeffs[:10]}...")
                print(f"    Distribution: min={min(slot_counts)}, max={max(slot_counts)}, diff={diff}")
                print(f"    Non-empty slots: {len(non_empty)}")
                print(f"\n[*] Polynomial coefficients:")
                print(','.join(map(str, coeffs)))
                
                # Save it
                with open('working_poly.txt', 'w') as f:
                    f.write(','.join(map(str, coeffs)))
                print(f"\n[+] Saved to working_poly.txt")
                
                exit(0)
    
    if attempt % 2000 == 0 and attempt > 0:
        print(f"    Progress: {attempt}/20000 attempts...")

print("\n[-] No polynomial found in 20000 attempts")
