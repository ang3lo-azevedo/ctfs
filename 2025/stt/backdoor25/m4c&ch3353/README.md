# m4c&ch3353 CTF Challenge - Backdoor CTF 2025

## Challenge Analysis

### Given Information
- Challenge: m4c&ch3353 (Mac and Cheese)
- Points: 499
- Author: jrke  
- Server: `nc remote.infoseciitr.in 4001`

### Challenge Description
"Prove that you have enough power to climb the tower snatch the partially broken treasure and fix it!"

### Code Analysis

The challenge implements a MAC verification system with the following components:

1. **Initialization**:
   - Generates `n` as a product of 16x 128-bit primes + powers of 2 (total 2048 bits)
   - Computes MAC as `CMAC(key=n[:16], message=n_as_bytes)`
   - Generates `base` as product of two 1024-bit primes
   - Provides MAC and signature

2. **Verification Challenge**:
   - Must provide N (2048 bits) and its prime factorization
   - All primes must be < 205 bits
   - Must satisfy: `CMAC(N[:16], N) == original_MAC`
   - If verified, can call `communicate()` to get encrypted flag

3. **The Problem**:
   - Need MAC collision: `CMAC(new_N) == CMAC(old_n)`
   - CMAC-AES collisions require ~2^64 attempts (birthday paradox)
   - Direct preimage attack requires ~2^128 attempts
   - Both are computationally infeasible with standard resources

### Attempted Approaches

1. **Random Brute Force**: Tested 10,000+ random combinations - no collision
2. **Fixed Base Variation**: Fixing some primes and varying others - no collision  
3. **Recovering Original n**: Not enough information from MAC + signature
4. **Code Bugs**: No obvious bugs found in verify() logic
5. **Same n Reuse**: Server generates new n each connection

### Possible Solutions

1. **Power Tower Vulnerability**: The `power_tower_mod` function (in `hidden.py`) might have exploitable weaknesses
2. **Mathematical Insight**: There might be a mathematical property of the construction that allows efficient collision finding
3. **Implementation Bug**: Subtle bug in CMAC implementation or usage
4. **Longer Computation**: MAC collision might be findable with more resources/time

### Key Observations

- The challenge emphasizes "power tower" and "climb the tower"
- Comment says power_tower_mod has "no vulnerabilities, trust me!!" (likely sarcastic)
- Flag is "partially broken" and needs to be "fixed"  
- After verification, original `n` and `data` are printed

### Current Status

**UNSOLVED** - Unable to find MAC collision or alternative path to verification.

The challenge likely requires either:
- Deep understanding of power tower mathematics
- Access to significant computational resources for brute force
- Discovery of a subtle vulnerability not yet identified

### Files Created

- `solve.py` / `solve2.py`: Initial solve attempts with MAC collision search
- `find_collision.py` / `find_collision2.py`: Brute force collision finders
- `test_verify.py`: Tests verification mechanism
- `check_static.py`: Checks if server reuses n
- Various analysis files documenting the investigation

### Next Steps

1. Research power tower properties and potential vulnerabilities
2. Look for CMAC-AES implementation weaknesses
3. Consider distributed computing for longer brute force
4. Search for CTF writeups if challenge is already solved
5. Ask for hints or collaborate with team

## Notes

This is a difficult cryptography challenge that appears to require either significant computational resources or a clever mathematical insight that hasn't been discovered yet.
