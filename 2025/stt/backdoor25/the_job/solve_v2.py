#!/usr/bin/env python3
from pwn import *

HOST = 'remote.infoseciitr.in'
PORT = 4006

def get_hash(num, coeff_arr, mod=10**9+7):
    """Replicate the hash function from the server"""
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % mod
        mult = (mult * num) % mod
    return hash_val

def find_working_polynomial(numbers, k=256, mod=10**9+7):
    """
    Find coefficients that distribute numbers evenly across k slots.
    
    Key constraints:
    - 896 numbers, 256 slots -> need 3 or 4 per slot
    - Hash must be < 256 for all numbers
    - Difference between max and min slot size must be < 2
    
    Approach: Build a Lagrange interpolation polynomial that maps
    each number to its assigned slot.
    """
    n = len(numbers)
    
    # Assign numbers to slots round-robin
    sorted_nums = sorted(numbers)
    assignments = {}
    for i, num in enumerate(sorted_nums):
        assignments[num] = i % k
    
    # Verify distribution
    slot_counts = [0] * k
    for num in numbers:
        slot_counts[assignments[num]] += 1
    
    print(f"[DEBUG] Target distribution: min={min(slot_counts)}, max={max(slot_counts)}, diff={max(slot_counts)-min(slot_counts)}")
    
    if max(slot_counts) - min(slot_counts) >= 2:
        print("[!] Warning: Round-robin doesn't give balanced distribution")
        # Try different assignment strategy
        slot_counts = [0] * k
        for i, num in enumerate(numbers):
            # Assign to least-full slot
            target = min(range(k), key=lambda s: slot_counts[s])
            assignments[num] = target
            slot_counts[target] += 1
        print(f"[DEBUG] Greedy distribution: min={min(slot_counts)}, max={max(slot_counts)}, diff={max(slot_counts)-min(slot_counts)}")
    
    # Now we need to build a polynomial with these mappings
    # For up to 896 points, we can use Lagrange interpolation
    # But that's complex to compute
    
    # Alternative: Since all numbers are known, we can use a lookup-table approach
    # encoded in the polynomial coefficients
    
    # Simpler: Just try some heuristic polynomials and see if they work
    # Let's compute what simple polynomials give us
    
    # Try: f(x) = 0 (all to slot 0)
    test_coeffs = [0]
    hashes = [get_hash(num, test_coeffs, mod) for num in numbers]
    if all(h < k for h in hashes):
        counts = [0] * k
        for h in hashes:
            counts[h] += 1
        print(f"[DEBUG] f(x)=0: min={min(counts)}, max={max(counts)}, diff={max(counts)-min(counts)}")
    
    # Try: f(x) = x (identity-ish)
    test_coeffs = [0, 1]
    hashes = [get_hash(num, test_coeffs, mod) for num in numbers]
    valid = all(h < k for h in hashes)
    if valid:
        counts = [0] * k
        for h in hashes:
            counts[h] += 1
        print(f"[DEBUG] f(x)=x: min={min(counts)}, max={max(counts)}, diff={max(counts)-min(counts)}, valid={valid}")
    else:
        print(f"[DEBUG] f(x)=x: produces hashes >= {k}")
    
    # The issue: numbers are random in [0, 10^9+7), so f(x)=x gives hashes that are too large
    
    # We need f(x) < 256 for all x in our set
    # One way: f(x) = c where c < 256 (constant function)
    # But this puts everything in one slot
    
    # Better: Use a high-degree polynomial with many small coefficients
    # that effectively encodes a lookup table
    
    # Actually, let's think about this differently:
    # We can use coefficients to encode information about each number
    
    # Hack: What if we use the numbers themselves as coefficients?
    # No, degree would be too high
    
    # Let me try a practical approach: Use multiple coefficient sets and test locally
    
    return None

def solve():
    io = remote(HOST, PORT)
    
    # Read initial text
    io.recvuntil(b"Press Enter to start > ")
    io.sendline(b"")
    
    # Get numbers
    io.recvuntil(b"Here are the leaked numbers : ")
    numbers_line = io.recvline().decode().strip()
    numbers = list(map(int, numbers_line.split(',')))
    
    print(f"[+] Received {len(numbers)} numbers")
    
    k = 256
    mod = 10**9 + 7
    
    # Find a working polynomial
    # After thinking: we need a polynomial where f(x) < 256 for all our x values
    # AND distributes them evenly
    
    # Key insight: We can use a polynomial with up to 895 coefficients!
    # We can encode almost arbitrary mappings
    
    # Simplest working approach for phase 1: 
    # Use many small coefficients to create pseudo-random but balanced hash
    
    # Let's try: coefficients [1, 2, 3, 4, ..., some pattern]
    # Or: all coefficients = 1
    
    # Try: f(x) = 1 + x + x^2 + ... (geometric series)
    # With small enough degree
    
    # Actually, let me just try a simple polynomial and see
    io.recvuntil(b"> ")
    
    # Try a polynomial with many small coefficients
    # This will create a "hash-like" function
    num_coeffs = 100
    coeffs = [1] * num_coeffs  # f(x) = 1 + x + x^2 + ... + x^99
    poly_str = ','.join(map(str, coeffs))
    
    print(f"[+] Trying polynomial with {num_coeffs} coefficients of value 1")
    io.sendline(poly_str.encode())
    
    # Check if it works
    try:
        response = io.recvuntil(b"Press Enter to continue > ", timeout=10)
        print(response.decode())
        
        if b"failed" in response or b"Faulty" in response:
            print("[-] Phase 1 failed!")
            io.close()
            return
        
        print("[+] Phase 1 passed!")
    except:
        print("[-] Timeout or error in phase 1")
        io.close()
        return
    
    io.sendline(b"")
    
    # Phase 2: Find the junk slot
    print("[+] Starting phase 2...")
    
    # Strategy: Use polynomials that distribute numbers to specific subsets of slots
    # Observe which distributions fail (meaning junk is in a filled slot)
    
    # With 256 slots and 6 tries, we can't do perfect binary search (need 8 bits)
    # But we can narrow it down significantly
    
    # Approach: For each trial, use a polynomial that fills a specific set of slots
    # Based on pass/fail, we learn where the junk is
    
    # Trial strategy: Fill slots based on bit patterns
    # Trial i: Fill slots where bit i is 0, leave slots where bit i is 1 empty
    
    # To fill specific slots: need to craft polynomial carefully
    # This is hard! Let's use a simpler approach:
    
    # Use constant polynomials to probe specific slots
    # But constant = c puts all 896 numbers in slot c
    # If junk is also in slot c, we have 897 total
    # Either way, the distribution is terrible (896 in one slot, 0-1 in others)
    # This always fails!
    
    # Better: We need polynomials that spread numbers across multiple slots
    # while leaving others empty
    
    # Idea: For trial i, use polynomial that fills slots [0, 2^i) evenly
    # and leaves [2^i, 256) empty
    # If junk is in [0, 2^i): fail (slot overload)
    # If junk is in [2^i, 256): pass (junk in empty slot)
    
    # To fill slots [0, m): use polynomial f(x) = (some_function(x)) mod m
    # But we need the result to be balanced within [0, m)
    
    # Implementation challenge: creating such polynomials on the fly
    
    # Let me try a simpler heuristic:
    # Use different random-looking polynomials and collect pass/fail patterns
    # Then deduce the junk slot
    
    results = []
    
    for trial in range(6):
        io.recvuntil(b"Enter the coefficients of the polynomial.\n> ")
        
        # Use different coefficient patterns for each trial
        # Trial i: use i+1 coefficients, all set to small values
        
        num_coeffs = trial + 1
        coeffs = [trial + 1] * num_coeffs
        poly_str = ','.join(map(str, coeffs))
        
        print(f"[+] Trial {trial+1}: polynomial with {num_coeffs} coefficients = {trial+1}")
        io.sendline(poly_str.encode())
        
        response = io.recvuntil(b"\n\n", timeout=5).decode()
        passed = "passed" in response
        results.append(passed)
        
        print(f"    Result: {'PASS' if passed else 'FAIL'}")
    
    # Analyze results to guess the junk slot
    # This is heuristic since we don't have a perfect strategy yet
    
    # For now, guess based on some pattern
    # If all pass: junk is in a slot that's never filled by our polynomials
    # If all fail: junk is in a commonly-filled slot
    
    # Make an educated guess
    if all(results):
        guess = 255  # High slot, might be empty
    elif not any(results):
        guess = 0  # Low slot, often filled
    else:
        # Mixed results, try to find pattern
        guess = results.index(True) if True in results else 0
    
    print(f"[+] Results: {results}")
    print(f"[+] Guessing slot: {guess}")
    
    io.recvuntil(b"Tell your friend the index : ")
    io.sendline(str(guess).encode())
    
    result = io.recvall(timeout=5).decode()
    print(result)
    
    io.close()

if __name__ == "__main__":
    solve()
