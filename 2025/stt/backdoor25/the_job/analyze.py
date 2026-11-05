#!/usr/bin/env python3
"""
Analyze the numbers and understand their distribution
"""

MOD = 10**9 + 7

# Load numbers
with open('numbers.txt', 'r') as f:
    numbers = list(map(int, f.read().strip().split(',')))

print(f"[+] Loaded {len(numbers)} numbers")

def get_hash(num, coeff_arr):
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % MOD
        mult = (mult * num) % MOD
    return hash_val

# Test what happens with f(x) = 1
print("\n[*] Testing f(x) = 1 (constant):")
coeffs = [1]
hashes = [get_hash(num, coeffs) for num in numbers]
print(f"    All hash to: {set(hashes)}")

# Test f(x) = 0 + 1*x = x
print("\n[*] Testing f(x) = x:")
coeffs = [0, 1]
hashes = [get_hash(num, coeffs) for num in numbers]
print(f"    Hash range: [{min(hashes)}, {max(hashes)}]")
print(f"    All < 256? {all(h < 256 for h in hashes)}")

# Check distribution of numbers themselves
print("\n[*] Analyzing number properties:")
mods_256 = [num % 256 for num in numbers]
from collections import Counter
freq = Counter(mods_256)
print(f"    Numbers mod 256: {len(freq)} unique values")
print(f"    Min frequency: {min(freq.values())}")
print(f"    Max frequency: {max(freq.values())}")
print(f"    Difference: {max(freq.values()) - min(freq.values())}")

if max(freq.values()) - min(freq.values()) < 2:
    print(f"    ✓ Numbers mod 256 gives balanced distribution!")
    
    # Now we need to find a polynomial where f(num) mod (10^9+7) = num mod 256
    # This is complex...
    
    print("\n[*] Testing if we can use modular arithmetic trick...")
    
    # Try f(x) = x mod 256 (but we need to express this as polynomial)
    # Actually, we can't directly do "x mod 256" in the polynomial
    
    # BUT: What if we use many coefficients?
    # With degree n-1 (895), we can potentially encode any mapping!
    
    print("    Need to use Lagrange interpolation or similar...")
    print("    This will take too long to compute directly.")
    
    print("\n[*] Trying heuristic: many small random coefficients...")
    
    import random
    random.seed(12345)
    
    for attempt in range(10000):
        length = random.randint(100, 500)
        coeffs = [random.randint(0, 10) for _ in range(length)]
        
        hashes = [get_hash(num, coeffs) for num in numbers]
        
        if all(h < 256 for h in hashes):
            # Check distribution
            slot_counts = [0] * 256
            for h in hashes:
                slot_counts[h] += 1
            
            non_empty = [c for c in slot_counts if c > 0]
            if len(non_empty) > 0:
                diff = max(non_empty) - min(non_empty)
                
                if diff < 2:
                    print(f"\n[+] FOUND WORKING POLYNOMIAL!")
                    print(f"    Length: {length}")
                    print(f"    Coefficients: {coeffs[:20]}...")
                    print(f"    Distribution: min={min(slot_counts)}, max={max(slot_counts)}, diff={diff}")
                    print(f"\n    Polynomial string:")
                    print(','.join(map(str, coeffs)))
                    break
        
        if attempt % 1000 == 0:
            print(f"    Attempt {attempt}/10000...")
    else:
        print("[-] No polynomial found in 10000 attempts")
