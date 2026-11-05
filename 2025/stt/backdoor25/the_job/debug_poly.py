#!/usr/bin/env python3
"""
Debug script to analyze the numbers and find a working polynomial offline
"""

from pwn import *

HOST = 'remote.infoseciitr.in'
PORT = 4006
MOD = 10**9 + 7

def get_hash(num, coeff_arr):
    hash_val = 0
    mult = 1
    for i in range(len(coeff_arr)):
        hash_val = (hash_val + mult * coeff_arr[len(coeff_arr)-1-i]) % MOD
        mult = (mult * num) % MOD
    return hash_val

def test_polynomial(numbers, coeffs, k=256):
    slot_counts = [0] * k
    
    for num in numbers:
        h = get_hash(num, coeffs)
        if h >= k:
            return False, None
        slot_counts[h] += 1
    
    max_per_slot = (len(numbers) + k - 1) // k
    if any(count > max_per_slot for count in slot_counts):
        return False, None
    
    non_empty = [c for c in slot_counts if c > 0]
    if len(non_empty) == 0:
        return False, None
    
    diff = max(non_empty) - min(non_empty)
    if diff >= 2:
        return False, None
    
    return True, (min(slot_counts), max(slot_counts), diff)

# Get numbers from server
print("[*] Connecting to get numbers...")
io = remote(HOST, PORT)
io.recvuntil(b"Press Enter to start > ")
io.sendline(b"")

io.recvuntil(b"Here are the leaked numbers : ")
numbers_line = io.recvline().decode().strip()
numbers = list(map(int, numbers_line.split(',')))

print(f"[+] Got {len(numbers)} numbers")

# Save them
with open('numbers.txt', 'w') as f:
    f.write(numbers_line)

print("[+] Saved to numbers.txt")

# Analyze the numbers
print(f"\n[*] Number statistics:")
print(f"    Min: {min(numbers)}")
print(f"    Max: {max(numbers)}")
print(f"    Range: {max(numbers) - min(numbers)}")

# Test simple polynomials locally
print("\n[*] Testing simple polynomials...")

# Try very simple ones first
for c in range(1, 200):
    coeffs = [c]
    works, stats = test_polynomial(numbers, coeffs)
    if works:
        print(f"[+] FOUND: f(x) = {c}")
        print(f"    Stats: {stats}")
        io.close()
        exit(0)

print("[!] No constant polynomial works, trying linear...")

# Try linear: f(x) = a + bx
for a in range(0, 100):
    for b in range(1, 50):
        coeffs = [a, b]
        works, stats = test_polynomial(numbers, coeffs)
        if works:
            print(f"[+] FOUND: f(x) = {a} + {b}x")
            print(f"    Stats: {stats}")
            io.close()
            exit(0)

print("[!] No linear polynomial works, trying quadratic...")

# Try quadratic
for a in range(0, 50):
    for b in range(0, 50):
        for c in range(0, 50):
            if a == 0 and b == 0 and c == 0:
                continue
            coeffs = [a, b, c]
            works, stats = test_polynomial(numbers, coeffs)
            if works:
                print(f"[+] FOUND: f(x) = {a} + {b}x + {c}x^2")
                print(f"    Stats: {stats}")
                io.close()
                exit(0)

print("[-] Could not find working polynomial with simple search")

io.close()
