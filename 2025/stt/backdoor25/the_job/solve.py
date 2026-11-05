#!/usr/bin/env python3
"""
The Job - CTF Solver

Key Mathematical Insights:
1. n=896 numbers, k=256 slots
2. Condition: len(slot[i]) <= (n+k-1)/k = 1151/256 ≈ 4.496, so max 4 per slot
3. Average: 896/256 = 3.5, so we need exactly 128 slots with 4 items, 128 slots with 3 items

Phase 1:
- Find polynomial where f(num) mod (10^9+7) < 256 for all numbers
- Distributes evenly: difference between max and min < 2

Phase 2:
- Junk value is placed DIRECTLY at slot[target] (not hashed!)
- Use 6 trials to find which of 256 slots contains junk
- Strategy: Use polynomials that map numbers to specific slot ranges
- If junk is in a filled slot: that slot exceeds limit (fail)
- If junk is in empty slot: distribution stays balanced (pass)
"""

from pwn import *
import sys

HOST = 'remote.infoseciitr.in'
PORT = 4006

def get_hash(num, coeff_arr, mod=10**9+7):
    """Replicate server's hash function"""
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % mod
        mult = (mult * num) % mod
    return hash_val

def test_polynomial(numbers, coeffs, k=256):
    """
    Test if a polynomial satisfies the phase 1 constraints:
    1. All hashes must be < K (256)
    2. Distribution must be balanced (max - min < 2)
    """
    slot_counts = [0] * k
    
    for num in numbers:
        h = get_hash(num, coeffs)
        if h >= k:
            return False, None
        slot_counts[h] += 1
    
    # Check per-slot limit
    max_per_slot = (len(numbers) + k - 1) // k  # = 4
    if any(count > max_per_slot for count in slot_counts):
        return False, None
    
    # Check balance (among non-empty slots)
    non_empty = [c for c in slot_counts if c > 0]
    if len(non_empty) == 0:
        return False, None
    
    diff = max(non_empty) - min(non_empty)
    if diff >= 2:
        return False, None
    
    return True, (min(slot_counts), max(slot_counts), diff)

def find_phase1_polynomial(numbers):
    """
    Search for a polynomial that satisfies phase 1 constraints.
    
    Strategy: Try patterns of small coefficients.
    The polynomial essentially acts as a hash function.
    """
    print("[*] Searching for phase 1 polynomial...")
    
    # Try increasing numbers of equal small coefficients
    for num_coeffs in range(1, 300):
        for val in range(1, 100):
            coeffs = [val] * num_coeffs
            works, stats = test_polynomial(numbers, coeffs)
            if works:
                print(f"[+] Found: {num_coeffs} coeffs of value {val}")
                print(f"    Stats: min={stats[0]}, max={stats[1]}, diff={stats[2]}")
                return coeffs
        
        # Progress indicator
        if num_coeffs % 50 == 0:
            print(f"    [Progress] Tested up to {num_coeffs} coefficients...")
    
    print("[-] Simple search failed, trying mixed patterns...")
    
    # Pattern 2: Alternating values
    for length in range(10, 200):
        for v1 in range(1, 30):
            for v2 in range(1, 30):
                coeffs = [v1 if i % 2 == 0 else v2 for i in range(length)]
                works, stats = test_polynomial(numbers, coeffs)
                if works:
                    print(f"[+] Found alternating pattern: {coeffs[:10]}...")
                    print(f"    Stats: min={stats[0]}, max={stats[1]}, diff={stats[2]}")
                    return coeffs
    
    print("[-] Alternating search failed, trying random patterns...")
    
    # Pattern 3: Random small coefficients
    import random
    random.seed(42)
    for attempt in range(5000):
        length = random.randint(20, 150)
        coeffs = [random.randint(1, 50) for _ in range(length)]
        works, stats = test_polynomial(numbers, coeffs)
        if works:
            print(f"[+] Found random pattern: {coeffs[:5]}... (length {length})")
            print(f"    Stats: min={stats[0]}, max={stats[1]}, diff={stats[2]}")
            return coeffs
        
        if attempt % 1000 == 0:
            print(f"    [Progress] Random attempt {attempt}/5000...")
    
    return None

def create_probe_poly(numbers, filled_slots, k=256, mod=10**9+7):
    """
    Create a polynomial that maps all numbers to specific slots.
    
    filled_slots: set of slot indices to fill
    Returns coefficients that distribute numbers among these slots
    """
    # We need to map all numbers to slots in filled_slots
    # And achieve balanced distribution within those slots
    
    num_target_slots = len(filled_slots)
    if num_target_slots == 0:
        return None
    
    # Calculate how many numbers per slot
    n = len(numbers)
    per_slot = n / num_target_slots
    
    # If per_slot > 4.496, this will fail even without junk
    if per_slot > 4.5:
        return None
    
    # Try to find coefficients that map to this range
    target_list = sorted(filled_slots)
    min_slot = min(target_list)
    max_slot = max(target_list)
    
    # Try simple patterns
    for num_coeffs in range(1, 50):
        for base in range(max(0, min_slot - 5), min_slot + 5):
            for mult in range(1, 10):
                coeffs = [base] + [mult] * (num_coeffs - 1)
                
                # Test if all numbers map to target slots
                all_match = True
                slot_counts = [0] * k
                
                for num in numbers:
                    h = get_hash(num, coeffs, mod)
                    if h not in filled_slots:
                        all_match = False
                        break
                    slot_counts[h] += 1
                
                if all_match:
                    # Check if balanced
                    counts_in_range = [slot_counts[s] for s in filled_slots]
                    if max(counts_in_range) - min(counts_in_range) < 2:
                        return coeffs
    
    return None

def solve():
    io = remote(HOST, PORT)
    
    # Get numbers
    io.recvuntil(b"Press Enter to start > ")
    io.sendline(b"")
    
    io.recvuntil(b"Here are the leaked numbers : ")
    numbers_line = io.recvline().decode().strip()
    numbers = list(map(int, numbers_line.split(',')))
    
    print(f"[+] Received {len(numbers)} numbers")
    print(f"[+] Target: {len(numbers)}/256 = {len(numbers)/256:.2f} per slot")
    print(f"[+] Max allowed per slot: {(len(numbers)+256-1)/256:.2f}")
    
    # Phase 1
    print("\n=== PHASE 1: Find balanced polynomial ===")
    
    coeffs = find_phase1_polynomial(numbers)
    
    if coeffs is None:
        print("[-] Could not find polynomial! Using fallback...")
        coeffs = [5] * 50  # Fallback
    
    poly_str = ','.join(map(str, coeffs))
    
    io.recvuntil(b"> ")
    io.sendline(poly_str.encode())
    
    try:
        response = io.recvuntil(b"Press Enter to continue > ", timeout=20)
        if b"failed" in response.lower() or b"faulty" in response.lower():
            print("[-] Phase 1 FAILED!")
            print(response.decode())
            io.close()
            return
        print("[+] Phase 1 PASSED!")
    except Exception as e:
        print(f"[-] Error: {e}")
        io.close()
        return
    
    io.sendline(b"")
    
    # Phase 2
    print("\n=== PHASE 2: Find junk slot (6 trials) ===")
    
    # Binary search strategy
    # We'll divide slots into ranges and test each
    # 256 slots, 6 trials -> can narrow to 256/2^6 = 4 candidates
    
    low = 0
    high = 255
    
    for trial in range(6):
        io.recvuntil(b"Enter the coefficients of the polynomial.\n> ")
        
        # Calculate range to test
        mid = (low + high) // 2
        
        print(f"\n[Trial {trial+1}] Range: [{low}, {high}], testing [{low}, {mid}]")
        
        # Strategy: Try to fill slots [low, mid] and leave [mid+1, high] empty
        # If junk is in [low, mid]: filled slot gets +1, might exceed limit -> FAIL
        # If junk is in [mid+1, high]: junk alone in empty slot -> PASS
        
        target_range = set(range(low, mid + 1))
        
        # Find polynomial that fills this range
        probe_coeffs = create_probe_poly(numbers, target_range)
        
        if probe_coeffs is None:
            # Fallback: use a simple pattern
            # This might not work perfectly, but let's try
            print(f"    [!] Could not create perfect probe, using heuristic")
            # Use a polynomial that might bias toward lower/upper range
            if trial % 2 == 0:
                probe_coeffs = [trial+1] * ((trial+1) * 5)
            else:
                probe_coeffs = [10-trial] * ((trial+1) * 5)
        
        poly_str = ','.join(map(str, probe_coeffs))
        io.sendline(poly_str.encode())
        
        response = io.recvuntil(b"\n\n", timeout=5).decode()
        passed = "passed" in response.lower()
        
        print(f"    Result: {'PASS' if passed else 'FAIL'}")
        
        # Update search range
        if passed:
            # Junk is NOT in [low, mid], must be in [mid+1, high]
            low = mid + 1
        else:
            # Junk IS in [low, mid]
            high = mid
        
        print(f"    Narrowed to: [{low}, {high}]")
        
        if low == high:
            print(f"    [+] Found exact slot: {low}")
            break
    
    # Make final guess
    guess = (low + high) // 2
    
    print(f"\n[+] Final guess: slot {guess}")
    
    io.recvuntil(b"Tell your friend the index : ")
    io.sendline(str(guess).encode())
    
    result = io.recvall(timeout=5).decode()
    print("\n" + "="*70)
    print(result)
    print("="*70)
    
    if "flag" in result.lower():
        print("\n🎉 SUCCESS! Got the flag!")
    else:
        print("\n❌ Failed to get flag")
    
    io.close()

if __name__ == "__main__":
    solve()
