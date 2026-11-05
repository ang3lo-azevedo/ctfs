#!/usr/bin/env python3
"""
XOR Prime RSA Challenge Solver

Strategy: recover p1, q1 bit-by-bit from LSB using constraints from N1 and N2.
For each candidate k value, check if a consistent solution exists.
"""

from Crypto.Util.number import long_to_bytes, isPrime

N1 = 77137069831818123807240774455950762767990413325793081508796360074912208684339628161427112820137604616364186817176929993166466430299619327344839882959001778451976753130205161851644854971151184622288638220974680166268249857500769241729148277129587383819591524571367295361146774816348936950289496781361622256443
N2 = 55257329876079913937467084112475373468177837748963935362332129789188857251800735356477517079143122141243407612092463419931588040889749099379431584939272391476247635032695559436249310025090918669634248311971318181756993765733583162339376948866195670567135163930175076492693764349661549726851793474969488819593
c = 58959278743937645851591382013760401753597451260953131216575517675841718487159634471812668046351886525599630606387992905969772305222532702273231458327776967101408551179284607382197009749321799536216946680372930943058129425282269200256091649631261562777705067403257726012903538791238687317454630715539764538584
e = 65537
l = 228  # q2 was generated with i=228

def solve_for_k(k, max_bits=512, max_candidates=5000):
    """Try to recover p1, q1 mod 2^b incrementally for a given k value."""
    candidates = {(1, 1)}  # Both primes are odd

    for bit in range(1, max_bits):
        mod = 1 << (bit + 1)
        new_candidates = set()
        n1_mod = N1 % mod
        n2_mod = N2 % mod

        for (p_low, q_low) in candidates:
            for pb in range(2):
                p_try = p_low | (pb << bit)
                for qb in range(2):
                    q_try = q_low | (qb << bit)
                    if (p_try * q_try) % mod != n1_mod:
                        continue

                    # Check N2 constraint
                    p_k = pow(p_try, k, mod)
                    q_k = pow(q_try, k, mod)
                    p_l = pow(p_try, l, mod)
                    q_l = pow(q_try, l, mod)

                    p2_low = ((p_k ^ q_k) + 1) % mod
                    q2_low = ((p_l ^ q_l) + 1) % mod

                    if (p2_low * q2_low) % mod != n2_mod:
                        continue

                    new_candidates.add((p_try, q_try))

        candidates = new_candidates
        if not candidates:
            return None
        
        if len(candidates) > max_candidates:
            return None  # Wrong k, candidates are not converging

    # Check full candidates
    results = []
    for (p1_cand, q1_cand) in candidates:
        if p1_cand * q1_cand == N1:
            results.append((p1_cand, q1_cand))
    
    return results if results else None


# Phase 1: Quick filter - find k values that survive at least 100 bits
print("Phase 1: Quick filtering k values (checking first 100 bits)...")
surviving_k = []

for k in range(1, l):
    result_or_none = solve_for_k(k, max_bits=100, max_candidates=500)
    if result_or_none is not None:
        # It returned a list (even if empty for intermediate results)
        surviving_k.append(k)
        print(f"  k={k} survived 100 bits")

if not surviving_k:
    print("No k values survived 100 bits. Trying with relaxed candidate limit...")
    for k in range(1, l):
        candidates = {(1, 1)}
        survived = True
        for bit in range(1, 100):
            mod = 1 << (bit + 1)
            new_candidates = set()
            n1_mod = N1 % mod
            n2_mod = N2 % mod

            for (p_low, q_low) in candidates:
                for pb in range(2):
                    p_try = p_low | (pb << bit)
                    for qb in range(2):
                        q_try = q_low | (qb << bit)
                        if (p_try * q_try) % mod != n1_mod:
                            continue
                        p_k = pow(p_try, k, mod)
                        q_k = pow(q_try, k, mod)
                        p_l = pow(p_try, l, mod)
                        q_l = pow(q_try, l, mod)
                        p2_low = ((p_k ^ q_k) + 1) % mod
                        q2_low = ((p_l ^ q_l) + 1) % mod
                        if (p2_low * q2_low) % mod != n2_mod:
                            continue
                        new_candidates.add((p_try, q_try))

            candidates = new_candidates
            if not candidates:
                survived = False
                break
        
        if survived:
            print(f"  k={k} survived 100 bits with {len(candidates)} candidates (no cap)")
            surviving_k.append(k)

print(f"\n{len(surviving_k)} k values survived phase 1")

# Phase 2: Run surviving k values to full 512 bits  
print("\nPhase 2: Full 512-bit recovery for surviving k values...")
for k in surviving_k:
    print(f"  Trying k={k}...")
    
    candidates = {(1, 1)}
    for bit in range(1, 512):
        mod = 1 << (bit + 1)
        new_candidates = set()
        n1_mod = N1 % mod
        n2_mod = N2 % mod

        for (p_low, q_low) in candidates:
            for pb in range(2):
                p_try = p_low | (pb << bit)
                for qb in range(2):
                    q_try = q_low | (qb << bit)
                    if (p_try * q_try) % mod != n1_mod:
                        continue
                    p_k = pow(p_try, k, mod)
                    q_k = pow(q_try, k, mod)
                    p_l = pow(p_try, l, mod)
                    q_l = pow(q_try, l, mod)
                    p2_low = ((p_k ^ q_k) + 1) % mod
                    q2_low = ((p_l ^ q_l) + 1) % mod
                    if (p2_low * q2_low) % mod != n2_mod:
                        continue
                    new_candidates.add((p_try, q_try))

        candidates = new_candidates
        if not candidates:
            print(f"    k={k} died at bit {bit}")
            break
        if bit % 100 == 0:
            print(f"    bit {bit}: {len(candidates)} candidates")
        if len(candidates) > 50000:
            print(f"    k={k} exploded at bit {bit}: {len(candidates)} candidates")
            break
    else:
        # Completed all 512 bits
        print(f"    k={k} completed! {len(candidates)} final candidates")
        for (p1, q1) in candidates:
            if p1 * q1 == N1:
                print(f"\nFOUND SOLUTION!")
                print(f"k = {k}")
                print(f"p1 = {p1}")
                print(f"q1 = {q1}")
                
                assert isPrime(p1)
                assert isPrime(q1)
                
                phi = (p1 - 1) * (q1 - 1)
                d = pow(e, -1, phi)
                m = pow(c, d, N1)
                flag = long_to_bytes(m)
                print(f"Flag: {flag}")
                try:
                    print(f"Flag (decoded): {flag.decode()}")
                except:
                    pass
                exit(0)
        print(f"    No candidate satisfies p1*q1 == N1 for k={k}")

print("\nNo solution found.")
