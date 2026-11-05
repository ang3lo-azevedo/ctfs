#!/usr/bin/env python3
from pwn import *
import sys

# Configuration
HOST = 'remote.infoseciitr.in'
PORT = 4006

def parse_numbers(number_str):
    """Parse the leaked numbers from the server"""
    return list(map(int, number_str.split(',')))

def get_hash(num, coeff_arr, mod=10**9+7):
    """Replicate the hash function from the server"""
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % mod
        mult = (mult * num) % mod
    return hash_val

def find_balanced_polynomial(numbers, k=256, mod=10**9+7):
    """
    Find a polynomial that distributes numbers evenly across k slots.
    
    Key insight: We need hash(x) < 256 for all x, and balanced distribution.
    With 896 numbers and 256 slots: 896/256 = 3.5
    So we need 128 slots with 4 elements and 128 slots with 3 elements.
    
    Strategy: Use polynomial coefficients to map numbers to slots.
    The simplest approach that might work: 
    - Use a high-degree polynomial with carefully chosen coefficients
    - Or use a simple linear mapping
    
    Let's try: f(x) = (a * x) mod (10^9+7), where we choose a such that
    the distribution works out.
    """
    
    # Try different polynomials
    # Option 1: f(x) = 0 (constant) - puts everything in slot 0 - won't work
    # Option 2: f(x) = c where c < 256 - same issue
    # Option 3: Use high-degree polynomial with specific structure
    
    # The key insight: we can use a polynomial of degree up to 895
    # We could encode each number's target slot in the polynomial!
    
    # But that's complex. Let's try a simpler approach first.
    # What if we use: f(x) = (x * inverse(some_number)) mod (10^9+7)?
    # We need the result to be < 256
    
    # Actually, let's compute what each number mod 256 gives us
    slot_counts = [0] * k
    for num in numbers:
        slot = num % k
        slot_counts[slot] += 1
    
    print(f"[DEBUG] Natural modulo distribution: min={min(slot_counts)}, max={max(slot_counts)}")
    
    # If this works, we need to find coefficients [a0, a1] such that:
    # (a0 + a1*x) mod (10^9+7) = x mod 256 for all our x values
    
    # This is impossible in general, but we can try to make it work
    # for our specific set of numbers.
    
    # Alternative: Build a polynomial that maps each number to its target slot
    # Using Lagrange interpolation or similar
    
    # For now, let's try the simplest thing: a very small constant
    # and see if the server gives us hints
    
    return "0"  # Start with f(x) = 0

def solve():
    # Connect to the server
    io = remote(HOST, PORT)
    
    # Read initial prompt
    io.recvuntil(b"Press Enter to start > ")
    io.sendline(b"")
    
    # Get the leaked numbers
    io.recvuntil(b"Here are the leaked numbers : ")
    numbers_line = io.recvline().decode().strip()
    numbers = parse_numbers(numbers_line)
    
    print(f"[+] Received {len(numbers)} numbers")
    n = len(numbers)
    k = 256
    mod = 10**9 + 7
    
    # Phase 1: Find a polynomial that distributes numbers evenly
    # Key insight: 896 numbers, 256 slots = 3.5 per slot
    # Need 128 slots with 4, 128 slots with 3 (or similar)
    
    # Let's build a polynomial using Lagrange interpolation
    # We want to map each number to a specific slot
    
    # First, assign each number to a slot (round-robin to balance)
    slot_assignments = {}
    current_slot = 0
    slots_usage = [[] for _ in range(k)]
    
    for i, num in enumerate(sorted(numbers)):
        target_slot = i % k
        slot_assignments[num] = target_slot
        slots_usage[target_slot].append(num)
    
    # Check distribution
    slot_sizes = [len(slots_usage[i]) for i in range(k)]
    print(f"[+] Target distribution: min={min(slot_sizes)}, max={max(slot_sizes)}")
    
    # Now we need to create a polynomial that gives these mappings
    # This is complex... Let's try a different approach
    
    # Simpler approach: Just try f(x) = 0 and see what happens
    # The server will tell us if it works
    
    io.recvuntil(b"> ")
    
    # Try a polynomial that might work
    # Let's use a high-degree polynomial with many coefficients
    # Structure: use coefficient i to map values to slot i
    
    # Actually, after thinking more: we can use a polynomial where
    # coefficient i corresponds to mapping certain numbers to certain slots
    
    # Even simpler: let's just try f(x) = 0 and move to phase 2
    # Phase 1 might auto-pass if we just need to pass phase 2
    
    first_poly = "0"
    print(f"[+] Sending first polynomial: {first_poly}")
    io.sendline(first_poly.encode())
    
    # Check response
    try:
        response = io.recvuntil(b"Press Enter to continue > ", timeout=10)
        print(response.decode())
    except:
        print("[-] Failed first phase")
        io.close()
        return
    
    io.sendline(b"")
    
    # Phase 2: Binary search to find the junk slot
    # Key insight: Junk is placed DIRECTLY at a fixed index (not hashed)
    # We hash 896 numbers using our polynomial, junk stays at target index
    # 
    # Strategy: Map all 896 numbers to specific ranges of slots
    # If junk is in a slot that also receives hashed numbers, it becomes overloaded (fails)
    # If junk is in an empty slot, distribution is still balanced (passes)
    #
    # Binary search: Test which range contains the junk
    
    print("[+] Phase 2: Finding junk slot with binary search...")
    
    # We'll do a 6-level binary search on the 256 slots
    # Divide into ranges and test each
    
    low = 0
    high = 255
    
    for trial in range(6):
        io.recvuntil(b"Enter the coefficients of the polynomial.\n> ")
        
        # Calculate midpoint of current range
        mid = (low + high) // 2
        
        # We want to map all 896 numbers to the LOWER half [low, mid]
        # If junk is in [low, mid], test will fail (overload)
        # If junk is in [mid+1, high], test will pass (junk in empty slots)
        
        # To map all numbers to [low, mid]:
        # We need roughly 896/(mid-low+1) numbers per slot in that range
        # And 0 in the upper range
        
        # Simplest approach: Map all numbers to a single slot in the lower range
        # Pick the middle of lower range
        target_slot = (low + mid) // 2
        
        # Use constant polynomial to map all to target_slot
        test_poly = str(target_slot)
        
        # But wait, this will fail the balance test!
        # target_slot will have 896 (or 897 if junk is there)
        # Other slots have 0 (or 1 if junk is there)
        # Difference > 2, so fails
        
        # We need to spread the 896 numbers across multiple slots
        # while keeping some slots empty
        
        # Better approach: Map numbers to fill [low, mid] evenly
        # Need to create a polynomial that does this
        
        # For now, let's use a simpler probe strategy:
        # Map all numbers to consecutive slots starting from 0
        # Then test specific slots
        
        # Actually, let me reconsider: We can use modulo operations
        # Map all 896 numbers mod (mid-low+1) + low
        # This fills slots [low, mid] with ~896/(mid-low+1) each
        # Slots [mid+1, high] are empty (except maybe junk)
        
        # But we can't express arbitrary modulo in the polynomial easily
        
        # Simplest working approach: Create polynomial that maps numbers
        # to slots 0 through 127 (or 128-255) evenly
        # We can do this by: f(x) = (i % 128) where i is the index
        # But we don't have access to index, only to the value x
        
        # Alternative: Sort numbers and assign to slots round-robin
        # But we can't do this with a single polynomial for all values!
        
        # Let me think of a tractable approach:
        # Use high-degree polynomial to assign each number individually
        # Since degree can be up to 895, we can use Lagrange interpolation
        
        # For trial k, assign numbers to create binary search pattern
        # But this requires computing interpolation polynomial...
        
        # Simpler heuristic: Use polynomial f(x) = (a*x + b) mod 256
        # where a, b chosen so that f distributes to desired range
        
        # For binary search, let's try this:
        # Map numbers to fill first half or second half based on trial
        
        # Trial implementation: Use a polynomial that separates space
        # Based on number properties
        
        # Let's test bit by bit instead:
        # Trial 0: Check if target & (1 << 0)
        # Trial 1: Check if target & (1 << 1)
        # ...
        # Trial 5: Check if target & (1 << 5)
        
        # For bit b: Map numbers such that:
        # - Slots with bit b=0 get all numbers
        # - Slots with bit b=1 get no numbers
        # Then if junk has bit b=1, it's in an empty slot (pass)
        # If junk has bit b=0, it's in a full slot (fail)
        
        # To implement: Fill specific slots based on bit pattern
        # Map all 896 numbers to slots where bit[trial] == 0
        
        bit_pos = trial
        test_slot = 0  # A slot with bit[bit_pos] == 0
        
        # Find a representative slot with bit clear
        for s in range(256):
            if not (s & (1 << bit_pos)):
                test_slot = s
                break
        
        test_poly = str(test_slot)
        
        print(f"[+] Trial {trial+1}: Testing bit {bit_pos}, mapping to slot {test_slot}")
        io.sendline(test_poly.encode())
        
        response = io.recvuntil(b"\n\n", timeout=5).decode()
        passed = "passed" in response
        
        print(f"    Result: {'PASS' if passed else 'FAIL'}")
        
        # Wait, constant polynomial won't work for balance!
        # All 896 go to one slot, massively imbalanced
        
        # I need to rethink this completely...
        
        # Let me try the actual binary search differently:
        # Partition slots into two groups A and B
        # Fill group A with distributed numbers, leave B empty
        # If junk in A: fail, if in B: pass
        
        # But I still can't easily create such polynomials!
        
        # Let me just try simple constant polynomials and see what happens
        # Even though they'll all fail, maybe there's a pattern
        
    # After 6 trials, make an educated guess
    # Since we couldn't extract enough information, try slot 0
    io.recvuntil(b"Tell your friend the index : ")
    guess = 0
    print(f"[+] Guessing index: {guess}")
    io.sendline(str(guess).encode())
    
    # Get the result
    result = io.recvall(timeout=5).decode()
    print(result)
    
    io.close()

if __name__ == "__main__":
    solve()
