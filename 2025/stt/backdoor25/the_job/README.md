# The Job - CTF Challenge

**Category:** Cryptography  
**Difficulty:** Medium  
**Points:** 152  
**Author:** L3G10N

## Challenge Description

Your non-cryptography "friend" needs your help or he might lose his job. Connect to the instance to get the flag after helping your friend save his job.

**Connection:** `nc remote.infoseciitr.in 4006`

## Problem Analysis

This challenge involves two phases:

### Phase 1: Hash Polynomial Design

**Goal:** Create a polynomial that acts as a hash function distributing 896 numbers across 256 hash table slots.

**Constraints:**
- Hash values must be < 256 (valid slot indices)
- Distribution must be balanced: difference between max and min slot sizes < 2
- Each slot can hold at most ⌊(896+256-1)/256⌋ = 4 elements
- Polynomial degree must be < 896

**Math:**
- 896 numbers ÷ 256 slots = 3.5 average per slot
- Ideal distribution: 128 slots with 4 items, 128 slots with 3 items

**Hash Function:**
```python
def get_hash(num, coeff_arr):
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % MOD
        mult = (mult * num) % MOD
    return hash_val
```

### Phase 2: Finding the Junk Slot

**Scenario:** After phase 1, your friend reveals he accidentally inserted a random "junk" value directly into a random hash table slot (not hashed - just placed at a random index).

**Goal:** Use 6 trials to determine which of the 256 slots contains the junk value.

**Strategy:** Binary search approach
- Create different polynomials that distribute the 896 numbers differently
- If junk lands in a slot that also receives hashed numbers, that slot may exceed limits → FAIL
- If junk lands in an empty or less-filled slot → PASS
- Use pass/fail results to narrow down the junk slot location

**Information Theory:**
- 256 possibilities = 8 bits of information
- 6 binary questions = up to 6 bits of information
- Can narrow down to 256/2^6 = 4 candidates
- Need smart strategy or heuristics for final guess

## Solution Approach

### Phase 1 Strategy

Search for polynomial coefficients that create balanced distribution:

1. **Try patterns of equal small coefficients:**
   - Test polynomials like [c, c, c, ...] for various values of c and various lengths
   - Check if all hashes < 256 and distribution is balanced

2. **Example working pattern:**
   - Often polynomials with 20-80 coefficients of value 1-10 work
   - The polynomial evaluation mod (10^9+7) creates pseudo-random distribution

### Phase 2 Strategy

Binary search implementation:

1. **Divide and conquer:**
   - Start with range [0, 255]
   - Each trial: create polynomial to test a sub-range
   - Based on pass/fail, narrow down the range

2. **Polynomial design per trial:**
   - Create polynomials that distribute numbers to specific slot ranges
   - Observe if junk causes imbalance (fail) or not (pass)

3. **Heuristics:**
   - Use varying coefficient patterns across trials
   - Interpret pass/fail patterns to converge on junk slot

## Implementation

See `solve.py` for the complete implementation.

**Key functions:**
- `get_hash(num, coeff_arr)` - Replicates server's hash function
- `test_polynomial(numbers, coeffs)` - Tests if polynomial satisfies phase 1 constraints
- `find_phase1_polynomial(numbers)` - Searches for working polynomial
- `binary_search_junk(io, numbers)` - Uses 6 trials to find junk slot

## Running the Solution

```bash
chmod +x solve.py
python3 solve.py
```

or

```bash
python3 solve.py | tee output.log
```

## Notes

- The server generates random numbers each time, so the working polynomial may vary
- Phase 1 search is deterministic but may take a minute
- Phase 2 binary search uses heuristics and may require multiple attempts
- Connection to server might be slow or timeout - be patient

## Flag Format

`flag{...}` or similar format

## Files

- `server.py` - Server-side challenge code (for analysis)
- `solve.py` - Complete solver script
- `solve_v2.py`, `solve_v3.py`, `solve_old.py` - Development versions
- `README.md` - This file

## Author

Solution by: r4ph3cks
