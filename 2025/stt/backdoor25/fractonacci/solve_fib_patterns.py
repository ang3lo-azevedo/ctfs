#!/usr/bin/env python3
"""
Alternative Fibonacci approach:
- Extract ALL LSB bits sequentially
- But decode them using Fibonacci-based grouping or skip patterns
"""
from PIL import Image

def fibonacci_sequence(n):
    """Generate first n Fibonacci numbers"""
    fibs = [1, 1]  # Start with 1, 1
    for i in range(n - 2):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

img = Image.open('challenge.png')
width, height = img.size

print(f"Image: {width}x{height}")

# Extract ALL LSB bits from red channel
print("Extracting all LSB bits from red channel...")
all_bits = []
for y in range(height):
    for x in range(width):
        pixel = img.getpixel((x, y))
        r = pixel[0]
        all_bits.append(r & 1)
    if y % 1000 == 0:
        print(f"  Progress: {y}/{height}")

print(f"Total bits extracted: {len(all_bits)}")

# Method 1: Skip bits according to Fibonacci sequence
print("\n" + "="*60)
print("Method 1: Read every Nth bit where N follows Fibonacci")
print("="*60)

fibs = fibonacci_sequence(30)
print(f"Fibonacci sequence: {fibs[:15]}")

for skip_pattern in [[1, 1, 2, 3, 5, 8], [1, 2, 3, 5, 8, 13], [2, 3, 5, 8, 13, 21]]:
    bits = []
    pos = 0
    skip_idx = 0
    
    while pos < min(len(all_bits), 100000):
        bits.append(all_bits[pos])
        pos += skip_pattern[skip_idx % len(skip_pattern)]
        skip_idx += 1
    
    if len(bits) >= 80:
        bytes_data = bytearray()
        for i in range(0, len(bits) - 7, 8):
            byte_val = sum(bits[i+j] << (7-j) for j in range(8))
            bytes_data.append(byte_val)
        
        text = bytes_data.decode('ascii', errors='ignore')
        
        if 'flag{' in text.lower():
            print(f"\n[+] FOUND with skip pattern {skip_pattern}!")
            idx = text.lower().find('flag{')
            end = text.find('}', idx)
            if end > idx:
                flag = text[idx:end+1]
                print(f"FLAG: {flag}\n")
                with open('FLAG.txt', 'w') as f:
                    f.write(flag)
        else:
            printable = sum(1 for c in text[:100] if c.isprintable() and c not in '\x00\xff')
            if printable > 30:
                print(f"Skip {skip_pattern}: {printable}/100 printable, sample: {text[:80]}")

# Method 2: Take bits at positions that are sums of Fibonacci numbers
print("\n" + "="*60)
print("Method 2: Positions that are Fibonacci sums")
print("="*60)

fib_set = set(fibs[:25])
bits = []
for i in range(min(len(all_bits), 200000)):
    if i in fib_set or (i % 100 in fib_set):
        bits.append(all_bits[i])

if len(bits) >= 80:
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    print(f"Extracted {len(bytes_data)} bytes")
    print(f"Sample: {text[:200]}")
    
    if 'flag{' in text.lower():
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"\n[+] FLAG: {flag}\n")

# Method 3: Start at Fibonacci offset
print("\n" + "="*60)
print("Method 3: Start reading from specific Fibonacci offset")
print("="*60)

for fib_offset in [233, 377, 610, 987, 1597, 2584]:
    bits = all_bits[fib_offset:fib_offset+8000]
    
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    
    if 'flag{' in text.lower():
        print(f"\n[+] FOUND at offset {fib_offset}!")
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"FLAG: {flag}\n")
            with open('FLAG.txt', 'w') as f:
                f.write(flag)
            break
    
    # Check for high printability
    printable = sum(1 for c in text[:500] if c.isprintable() and c not in '\x00\xff')
    if printable > 200:
        print(f"Offset {fib_offset}: {printable}/500 printable")
        print(f"  Sample: {text[:100]}")

print("\nDone checking Fibonacci-based extraction methods")
