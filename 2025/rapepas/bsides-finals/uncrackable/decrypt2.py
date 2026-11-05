from Crypto.Util.number import long_to_bytes
from math import gcd

E = 17
P = 11597166774805816360374533222160956809018404723840861522383308499395527627290774469823379311117296851267206314487641873943180659565217684541916875624211057
Q = 10299259347747928961347916710965884793566467500379338565611709756580084514797750477528235783072393737268858330173161937900575641691604309487247972127007029
N = P * Q
C = 83298786517649178994322985245600428376509252851731063654371829263180374790079738871415746182154258028025689198568496601569647770368552771110345801359579206806945452488275246543002394288454091984709467169986485096007711920555686754316356858281224646787700911502582512038052611011696309902163943650177921635654

def main() -> None:
    # Calculate phi(n) = (p-1)(q-1)
    phi = (P - 1) * (Q - 1)
    
    # Check if e and phi are coprime
    g = gcd(E, phi)
    print(f"gcd(e, phi) = {g}")
    
    if g != 1:
        print(f"\nE={E} shares a common factor with phi(n)!")
        print(f"This means RSA is broken!")
        
        # When gcd(e, phi) != 1, we can't compute the standard d
        # But we can still decrypt using a different approach
        
        # Since e = 17 and gcd(e, phi) = 17, this means 17 divides phi
        # We can compute the e-th root modulo n using CRT
        
        # Let's try a different approach: compute m^e ≡ c (mod n)
        # We need to find the e-th root of c modulo n
        
        # Using Tonelli-Shanks or other root finding algorithms
        # But first, let's check if we can work with the factors
        
        # Compute c^((p-1)/e) mod p and c^((q-1)/e) mod q
        # if e divides p-1 and q-1
        
        print(f"\n(P-1) % E = {(P-1) % E}")
        print(f"(Q-1) % E = {(Q-1) % E}")
        
        # Both are divisible by 17!
        # We can compute the e-th root using CRT
        
        # For prime p where e | (p-1), we can compute e-th roots
        # m_p = c^(d_p) mod p where d_p = ((p-1)/e + 1)
        # But this might give us multiple roots
        
        # Let's try a simpler approach: brute force with Chinese Remainder Theorem
        # Since e = 17 is small, there are at most 17^2 = 289 possible values
        
        print("\nTrying to find all possible roots modulo P and Q...")
        
        # Find all 17-th roots of C modulo P
        roots_p = []
        for i in range(E):
            # Compute a potential root
            exp = ((P - 1) // E * i + 1)
            root = pow(C, exp, P)
            if pow(root, E, P) == C % P:
                roots_p.append(root)
        
        # Find all 17-th roots of C modulo Q
        roots_q = []
        for i in range(E):
            exp = ((Q - 1) // E * i + 1)
            root = pow(C, exp, Q)
            if pow(root, E, Q) == C % Q:
                roots_q.append(root)
        
        print(f"Found {len(roots_p)} roots mod P")
        print(f"Found {len(roots_q)} roots mod Q")
        
        # Use CRT to combine roots
        print("\nTrying all combinations with CRT...")
        for rp in roots_p:
            for rq in roots_q:
                # Chinese Remainder Theorem
                # m ≡ rp (mod P)
                # m ≡ rq (mod Q)
                # m = rp + P * ((rq - rp) * inv(P, Q) mod Q)
                m = (rp + P * ((rq - rp) * pow(P, -1, Q) % Q)) % N
                
                # Verify
                if pow(m, E, N) == C:
                    try:
                        flag = long_to_bytes(m)
                        if b'BSides' in flag or b'FLAG' in flag or b'{' in flag:
                            print(f"\nFlag found: {flag.decode()}")
                            return
                    except:
                        pass

if __name__ == "__main__":
    main()
