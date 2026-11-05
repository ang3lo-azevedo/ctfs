from Crypto.Hash import CMAC
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long, getPrime

def compute_mac(n):
    x = long_to_bytes(n)
    # Pad to at least 16 bytes for AES key
    if len(x) < 16:
        x = b'\x00' * (16 - len(x)) + x
    print(f"n has {len(x)} bytes, first 16 bytes: {x[:16].hex()}")
    cc = CMAC.new(x[:16], ciphermod=AES)
    return cc.update(x).hexdigest()

# Test with small numbers
print("Testing MAC computation:\n")

# Test 1: Large enough number  
n1 = 2**128 + 12345
mac1 = compute_mac(n1)
print(f"n1 = 2^128 + 12345")
print(f"MAC = {mac1}\n")

# Test 2: 2048-bit number with powers of 2
n2 = 2**2047
mac2 = compute_mac(n2)
print(f"n2 = 2^2047 (2048 bits)")
print(f"MAC = {mac2}\n")

# Test 3: Different 2048-bit number
n3 = 2**2047 + 1
mac3 = compute_mac(n3)
print(f"n3 = 2^2047 + 1")
print(f"MAC = {mac3}\n")

# Test 4: Random 2048-bit number
p1 = getPrime(1024)
p2 = getPrime(1024)
n4 = p1 * p2
mac4 = compute_mac(n4)
print(f"n4 = random 2048-bit composite")
print(f"MAC = {mac4}\n")

# The key insight: Can we construct two different numbers with the same MAC?
# This requires either:
# 1. Same first 16 bytes AND same overall CMAC
# 2. Or exploiting some property of CMAC

print("=" * 60)
print("Key question: How feasible is a MAC collision?")
print("- MAC space: 128 bits (2^128)")
print("- Our search space: 2048-bit numbers with specific structure")
print("- Birthday paradox applies")
print("- Expected collisions after ~2^64 attempts (not feasible)")
print("=" * 60)
