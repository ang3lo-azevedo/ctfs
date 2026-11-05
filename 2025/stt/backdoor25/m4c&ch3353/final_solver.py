#!/usr/bin/env python3
"""
Comprehensive solver for m4c&ch3353 challenge

This script provides multiple solving strategies and can be extended
as new insights are discovered.
"""

from pwn import *
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, getPrime, isPrime
import sys
import random

context.log_level = 'info'

def compute_mac(n):
    """Compute CMAC of n using first 16 bytes as key"""
    x = long_to_bytes(n)
    cc = CMAC.new(x[:16], ciphermod=AES)
    return cc.update(x).hexdigest()

def build_n(prime_list, target_bits=2048):
    """Build n from list of (prime, count) tuples"""
    n = 1
    data = []
    for p, count in prime_list:
        n *= pow(p, count)
        data.append([p, count])
    
    # Pad with 2s if needed
    twos = 0
    while n.bit_length() < target_bits:
        n *= 2
        twos += 1
    
    if twos > 0:
        data.append([2, twos])
    
    return n, data

class Solver:
    def __init__(self, target_mac, signature):
        self.target_mac = target_mac
        self.signature = signature
        self.target_bits = 2048
        self.max_prime_bits = 204
        
    def strategy_1_random_search(self, max_attempts=10000):
        """Strategy 1: Random prime combinations"""
        log.info("Strategy 1: Random search with varied prime sizes")
        
        # Generate prime pool
        prime_pool = []
        for bits in [100, 120, 140, 160, 180, 200]:
            for _ in range(10):
                prime_pool.append(getPrime(bits))
        
        for attempt in range(max_attempts):
            num_primes = random.randint(5, 12)
            primes = [(p, 1) for p in random.sample(prime_pool, num_primes)]
            
            n, data = build_n(primes)
            
            if n.bit_length() != self.target_bits:
                continue
            
            mac = compute_mac(n)
            
            if attempt % 100 == 0:
                log.info(f"Attempt {attempt}: MAC={mac[:16]}...")
            
            if mac == self.target_mac:
                log.success("COLLISION FOUND!")
                return n, data
        
        return None, None
    
    def strategy_2_systematic_search(self):
        """Strategy 2: Systematic exploration of prime structures"""
        log.info("Strategy 2: Systematic prime structure exploration")
        
        # Try specific structures that might have patterns
        structures = [
            # (num_primes, [bit_sizes])
            (10, [200]*10),
            (11, [185]*11),
            (12, [170]*12),
            (8, [200, 200, 200, 180, 180, 180, 160, 160]),
        ]
        
        for structure_idx, (num, bit_sizes) in enumerate(structures):
            log.info(f"Testing structure {structure_idx+1}/{len(structures)}")
            
            for attempt in range(1000):
                primes = [(getPrime(bits), 1) for bits in bit_sizes]
                n, data = build_n(primes)
                
                if n.bit_length() != self.target_bits:
                    continue
                
                mac = compute_mac(n)
                
                if mac == self.target_mac:
                    log.success("COLLISION FOUND!")
                    return n, data
        
        return None, None
    
    def strategy_3_power_of_two_variation(self):
        """Strategy 3: Vary power of 2 exponent"""
        log.info("Strategy 3: Power of 2 variation")
        
        # Fixed set of large primes, vary 2^k
        base_primes = [getPrime(200) for _ in range(10)]
        
        for k in range(1, 500):
            primes = [(p, 1) for p in base_primes] + [(2, k)]
            n = 1
            for p, count in primes:
                n *= pow(p, count)
            
            if n.bit_length() != self.target_bits:
                continue
            
            mac = compute_mac(n)
            data = [[p, c] for p, c in primes]
            
            if mac == self.target_mac:
                log.success("COLLISION FOUND!")
                return n, data
        
        return None, None
    
    def interactive_explore(self, io):
        """Interactive exploration mode"""
        log.info("Interactive exploration mode")
        log.info("This will test various approaches with the server")
        
        # Try to gather more information
        log.info("Testing obfuscateSmall to gather information...")
        
        for i in range(min(10, 90)):  # Save some steps
            io.recvuntil(b'Choose: ')
            io.sendline(b'3')
            io.recvuntil(b'Enter your message : ')
            io.sendline(str(1 << i).encode())
            io.recvuntil(b'Here is your obfuscated message :  ')
            result = int(io.recvline().strip())
            if i < 3:
                log.info(f"obfuscateSmall(2^{i}) = {result}")
        
        log.info("Information gathered. Switching to interactive mode.")
        io.interactive()

def main():
    # Connect to server
    io = remote('remote.infoseciitr.in', 4001)
    
    # Get target values
    io.recvuntil(b'My m4c&ch3353: ')
    mac = io.recvline().strip().decode()
    log.success(f"Target MAC: {mac}")
    
    io.recvuntil(b'My signature:  ')
    signature = int(io.recvline().strip().decode())
    log.success(f"Signature: {signature}")
    
    solver = Solver(mac, signature)
    
    print("\n" + "="*60)
    print("Available strategies:")
    print("1. Random search (10k attempts)")
    print("2. Systematic structure search")
    print("3. Power of 2 variation")
    print("4. Interactive exploration")
    print("5. All strategies in sequence")
    print("="*60)
    
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = '4'  # Default to interactive
    
    n, data = None, None
    
    if choice == '1':
        n, data = solver.strategy_1_random_search()
    elif choice == '2':
        n, data = solver.strategy_2_systematic_search()
    elif choice == '3':
        n, data = solver.strategy_3_power_of_two_variation()
    elif choice == '4':
        solver.interactive_explore(io)
        return
    elif choice == '5':
        for strat_name, strat_func in [
            ("Random", solver.strategy_1_random_search),
            ("Systematic", solver.strategy_2_systematic_search),
            ("Pow2", solver.strategy_3_power_of_two_variation),
        ]:
            log.info(f"Trying {strat_name} strategy...")
            n, data = strat_func()
            if n:
                break
    
    if n and data:
        # Submit verification
        log.success("Submitting collision for verification...")
        io.recvuntil(b'Choose: ')
        io.sendline(b'2')
        io.recvuntil(b'Give me the MY modulus : ')
        io.sendline(str(n).encode())
        io.recvuntil(b'Enter prime factorization')
        format_str = '-'.join([f"[{p}, {c}]" for p, c in data])
        io.sendline(format_str.encode())
        
        response = io.recvline().decode()
        log.info(f"Response: {response}")
        
        if "verified" in response.lower():
            log.success("VERIFICATION SUCCESSFUL!")
            io.recvuntil(b'Choose: ')
            io.sendline(b'1')
            io.interactive()
        else:
            log.error("Verification failed")
    else:
        log.error("No collision found")
        log.info("Switching to interactive mode for manual exploration")
        io.interactive()

if __name__ == '__main__':
    main()
