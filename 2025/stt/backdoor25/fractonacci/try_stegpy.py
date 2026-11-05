#!/usr/bin/env python3
"""
Try using stegano library for extraction
"""
import sys

try:
    from stegano import lsb
    print("Trying stegano.lsb.reveal...")
    secret = lsb.reveal("challenge.png")
    if secret:
        print(f"\n[+] Found hidden message:\n{secret}\n")
        if 'flag{' in secret.lower() or 'backdoor{' in secret.lower():
            print(f"[+] FLAG: {secret}")
            with open('FLAG_FOUND.txt', 'w') as f:
                f.write(secret)
    else:
        print("No hidden message found with stegano.lsb")
except ImportError:
    print("stegano not installed, trying manual methods...")
except Exception as e:
    print(f"stegano error: {e}")

# Try stegpy
try:
    import subprocess
    result = subprocess.run(['stegpy', 'challenge.png', '-o', 'output_stegpy.txt'], 
                          capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        print("\n[+] stegpy extraction successful")
        with open('output_stegpy.txt', 'r') as f:
            content = f.read()
            print(content[:500])
            if 'flag{' in content.lower():
                print(f"\n[+] FLAG FOUND: {content}")
except Exception as e:
    print(f"stegpy not available: {e}")

# Try PIL-based method with different bit combinations
from PIL import Image
import numpy as np

img = Image.open('challenge.png')
arr = np.array(img)

print("\n" + "="*60)
print("Trying combinations of multiple LSB bits")
print("="*60)

for num_bits in [1, 2, 3, 4]:
    bits = []
    red = arr[:, :, 0]
    
    # Extract multiple LSBs
    for y in range(min(1000, arr.shape[0])):  # First 1000 rows
        for x in range(min(1000, arr.shape[1])):
            for bit_pos in range(num_bits):
                bits.append((red[y, x] >> bit_pos) & 1)
    
    # Convert to bytes
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    
    if 'flag{' in text.lower():
        print(f"\n[+] FOUND with {num_bits} bits!")
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"FLAG: {flag}")
            with open('FLAG_FOUND.txt', 'w') as f:
                f.write(flag)
            sys.exit(0)
    
    printable = sum(1 for c in text[:200] if c.isprintable() and c not in '\x00\xff')
    if printable > 50:
        print(f"{num_bits} bits: {printable}/200 printable, sample: {text[:60]}")

print("\nNo flag found in standard extractions")
