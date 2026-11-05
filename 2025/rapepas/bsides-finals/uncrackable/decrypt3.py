from Crypto.Util.number import long_to_bytes
from math import gcd

E = 17
P = 11597166774805816360374533222160956809018404723840861522383308499395527627290774469823379311117296851267206314487641873943180659565217684541916875624211057
Q = 10299259347747928961347916710965884793566467500379338565611709756580084514797750477528235783072393737268858330173161937900575641691604309487247972127007029
N = P * Q
C = 83298786517649178994322985245600428376509252851731063654371829263180374790079738871415746182154258028025689198568496601569647770368552771110345801359579206806945452488275246543002394288454091984709467169986485096007711920555686754316356858281224646787700911502582512038052611011696309902163943650177921635654

def find_eth_roots_mod_p(c, e, p):
    """Find all e-th roots of c modulo prime p"""
    # Check if c is 0
    if c % p == 0:
        return [0]
    
    # For prime p, if e | (p-1), there are e possible e-th roots
    if (p - 1) % e != 0:
        # e doesn't divide p-1, compute the inverse normally
        d = pow(e, -1, p - 1)
        return [pow(c, d, p)]
    
    # e divides p-1, so we need to find all e-th roots
    # Find a generator g of the multiplicative group mod p
    # and express c and potential roots in terms of g
    
    # For simplicity, let's brute force search for small e
    # Or use a more sophisticated approach
    
    # Actually, let's use a different method:
    # Write p-1 = e^k * m where gcd(e, m) = 1
    p_minus_1 = p - 1
    k = 0
    m = p_minus_1
    while m % e == 0:
        k += 1
        m //= e
    
    # Now p-1 = e^k * m
    # Compute d = e^(-1) mod m
    d = pow(e, -1, m)
    
    # One root is c^d mod p
    root = pow(c, d, p)
    
    # To find other roots, we need a primitive e-th root of unity
    # Find an element of order e
    # w^e ≡ 1 (mod p) and w != 1
    
    # Find a generator of order e
    # We need g^((p-1)/e) which has order e
    for g in range(2, min(1000, p)):
        w = pow(g, (p - 1) // e, p)
        if w != 1:
            # Found a primitive e-th root of unity
            roots = []
            current = root
            for i in range(e):
                roots.append(current)
                current = (current * w) % p
                if current == root:
                    break
            return roots
    
    return [root]

def main() -> None:
    # Calculate phi(n) = (p-1)(q-1)
    phi = (P - 1) * (Q - 1)
    
    # Check if e and phi are coprime
    g = gcd(E, phi)
    print(f"gcd(e, phi) = {g}")
    print(f"(P-1) % E = {(P-1) % E}")
    print(f"(Q-1) % E = {(Q-1) % E}")
    
    # Find roots modulo P and Q
    print("\nFinding e-th roots...")
    roots_p = find_eth_roots_mod_p(C, E, P)
    roots_q = find_eth_roots_mod_p(C, E, Q)
    
    print(f"Found {len(roots_p)} roots mod P")
    print(f"Found {len(roots_q)} roots mod Q")
    
    # Use CRT to combine roots
    print("\nTrying all combinations with CRT...")
    valid_flags = []
    
    for rp in roots_p:
        for rq in roots_q:
            # Chinese Remainder Theorem
            # m ≡ rp (mod P)
            # m ≡ rq (mod Q)
            m = (rp + P * ((rq - rp) * pow(P, -1, Q) % Q)) % N
            
            # Verify
            if pow(m, E, N) == C:
                try:
                    flag = long_to_bytes(m)
                    decoded = flag.decode('utf-8', errors='ignore')
                    if any(c.isprintable() for c in decoded):
                        valid_flags.append(decoded)
                        print(f"Potential flag: {decoded}")
                except:
                    pass
    
    if valid_flags:
        print(f"\n{'='*60}")
        print("VALID FLAGS:")
        for flag in valid_flags:
            print(flag)

if __name__ == "__main__":
    main()
