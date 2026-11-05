from pwn import *
from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long, isPrime, getPrime
import itertools

# Connect to remote
io = remote('remote.infoseciitr.in', 4001)

# Receive initial values
io.recvuntil(b'My m4c&ch3353: ')
mac = io.recvline().strip().decode()
print(f"[+] MAC: {mac}")

io.recvuntil(b'My signature:  ')
signature = int(io.recvline().strip().decode())
print(f"[+] Signature: {signature}")

"""
Key insights:
1. CMAC uses n converted to bytes, but only first 16 bytes as AES key: x[:16]
2. Then it computes CMAC of the entire x
3. We need to find a different N with same MAC
4. N must be 2048 bits (2 * 1024)
5. N must be product of primes, each prime < 204 bits (1024/5)

The vulnerability: We can brute force the first 16 bytes to match the MAC
Then pad with small primes to reach 2048 bits
"""

def compute_mac(n_bytes):
    """Compute CMAC of n_bytes using first 16 bytes as key"""
    cc = CMAC.new(n_bytes[:16], ciphermod=AES)
    return cc.update(n_bytes).hexdigest()

def find_mac_collision(target_mac, target_bits=2048, max_prime_bits=204):
    """
    Find an N that produces the same MAC
    Strategy: Brute force first 16 bytes, then pad with primes
    """
    print("\n[*] Searching for MAC collision...")
    
    # We need to find first 16 bytes such that when we pad to 2048 bits,
    # the resulting MAC matches
    
    # Start with small primes
    from Crypto.Util.number import getPrime
    
    attempts = 0
    while True:
        attempts += 1
        if attempts % 10 == 0:
            print(f"[*] Attempt {attempts}...")
        
        # Generate N from small primes
        primes_data = []
        n = 1
        
        # Build up to target bits with primes under max_prime_bits
        while n.bit_length() < target_bits - 10:
            p = getPrime(min(max_prime_bits, target_bits - n.bit_length()))
            count = 1
            primes_data.append([p, count])
            n *= p
        
        # Pad with 2s to reach exact bit length
        twos_count = 0
        while n.bit_length() < target_bits:
            n *= 2
            twos_count += 1
        
        if twos_count > 0:
            primes_data.append([2, twos_count])
        
        # Check if this gives us the right MAC
        n_bytes = long_to_bytes(n)
        current_mac = compute_mac(n_bytes)
        
        if current_mac == target_mac:
            print(f"[+] Found collision after {attempts} attempts!")
            return n, primes_data
        
        # If not exact 2048 bits, skip
        if n.bit_length() != target_bits:
            continue
        
        # Try small variations
        if attempts > 100:
            break
    
    return None, None

print("\n[*] Attempting to find MAC collision...")

# Try a different approach: use the power_tower function before verification
# to understand the structure of n

# First, let's leak information using option 3
print("\n[*] Leaking key information via obfuscation...")

keys_info = []
for i in range(96):
    test_val = 1 << i
    io.recvuntil(b'Choose: ')
    io.sendline(b'3')
    io.recvuntil(b'Enter your message : ')
    io.sendline(str(test_val).encode())
    io.recvuntil(b'Here is your obfuscated message :  ')
    result = int(io.recvline().strip())
    # result = test_val (with high bits cleared) + keys[i]
    # Since test_val only has bit i set in low 96 bits
    # result - 0 = keys[i]
    keys_info.append(result)
    if i < 5:
        print(f"[+] key[{i}] leaked: {result}")

print(f"[*] Leaked {len(keys_info)} keys")

# Now try to forge verification
# We'll try a simple approach: generate N with small primes
print("\n[*] Generating forged N...")

n_forge, primes_data = find_mac_collision(mac)

if n_forge and primes_data:
    print(f"[+] Forged N: {n_forge}")
    print(f"[+] Prime factorization has {len(primes_data)} terms")
    
    # Send verification
    io.recvuntil(b'Choose: ')
    io.sendline(b'2')
    io.recvuntil(b'Give me the MY modulus : ')
    io.sendline(str(n_forge).encode())
    io.recvuntil(b'Enter prime factorization in format')
    
    # Format: [prime1, count1]-[prime2, count2]-...
    format_str = '-'.join([f"[{p}, {c}]" for p, c in primes_data])
    io.sendline(format_str.encode())
    
    response = io.recvline()
    print(f"[*] Verification response: {response}")
else:
    print("[-] Could not find MAC collision, trying direct approach...")
    io.interactive()

io.interactive()
