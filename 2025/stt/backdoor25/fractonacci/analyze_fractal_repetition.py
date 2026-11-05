#!/usr/bin/env python3
"""
Analyze the fractal repetition pattern
Fractals repeat at different scales - use Fibonacci to determine the scales
"""
from PIL import Image
import numpy as np

def fibonacci_sequence(n):
    """Generate first n Fibonacci numbers"""
    fibs = [1, 1]
    for i in range(n - 2):
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

img = Image.open('challenge.png')
arr = np.array(img)
red = arr[:, :, 0]
h, w = red.shape

print(f"Image: {w}x{h}")
print("Analyzing fractal repetition patterns...")

# Fractals repeat at different scales
# Try extracting LSB from pixels at Fibonacci-scaled distances from center
center_x, center_y = w // 2, h // 2

fibs = fibonacci_sequence(25)
print(f"Fibonacci scales: {fibs[:15]}")

# Method 1: Sample at Fibonacci radii with Fibonacci angular steps
print("\n" + "="*60)
print("Method 1: Fractal sampling at Fibonacci scales")
print("="*60)

bits = []
for radius in fibs[2:20]:  # Skip 1,1
    if radius >= min(w, h) // 2:
        break
    
    # Number of samples = Fibonacci number
    num_samples = radius if radius < 100 else 100
    
    for i in range(num_samples):
        angle = 2 * np.pi * i / num_samples
        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))
        
        if 0 <= x < w and 0 <= y < h:
            bits.append(red[y, x] & 1)

print(f"Extracted {len(bits)} bits")

if len(bits) >= 80:
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    print(f"Sample: {text[:200]}")
    
    if 'flag{' in text.lower():
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"\n[+] FLAG: {flag}\n")
            with open('FLAG.txt', 'w') as f:
                f.write(flag)

# Method 2: The golden angle (related to Fibonacci) - 137.5 degrees
print("\n" + "="*60)
print("Method 2: Golden angle spiral (Fibonacci spiral)")
print("="*60)

golden_angle = 137.5 * np.pi / 180  # Golden angle in radians

bits = []
for i in range(10000):
    angle = i * golden_angle
    # Distance grows with square root (phyllotaxis pattern)
    radius = 3 * np.sqrt(i)
    
    x = int(center_x + radius * np.cos(angle))
    y = int(center_y + radius * np.sin(angle))
    
    if 0 <= x < w and 0 <= y < h:
        bits.append(red[y, x] & 1)
    else:
        break

print(f"Extracted {len(bits)} bits using golden angle spiral")

if len(bits) >= 80:
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    print(f"Sample: {text[:200]}")
    
    if 'flag{' in text.lower():
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"\n[+] FLAG: {flag}\n")
            with open('FLAG.txt', 'w') as f:
                f.write(flag)

# Method 3: Fractal self-similarity - compare different scale levels
print("\n" + "="*60)
print("Method 3: Extract from fractal 'petals' at each level")
print("="*60)

# The fractal has 6 or 8 petals - try extracting from petal centers
num_petals = 8

bits = []
for level_idx, radius in enumerate(fibs[3:18]):
    if radius >= min(w, h) // 2:
        break
    
    # Extract from each petal at this level
    for petal in range(num_petals):
        angle = 2 * np.pi * petal / num_petals
        
        # Sample a few points along each petal
        for dist in [radius * 0.8, radius, radius * 1.2]:
            x = int(center_x + dist * np.cos(angle))
            y = int(center_y + dist * np.sin(angle))
            
            if 0 <= x < w and 0 <= y < h:
                bits.append(red[y, x] & 1)

print(f"Extracted {len(bits)} bits from petal structure")

if len(bits) >= 80:
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    print(f"Sample: {text[:200]}")
    
    if 'flag{' in text.lower():
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"\n[+] FLAG: {flag}\n")
            with open('FLAG.txt', 'w') as f:
                f.write(flag)

# Method 4: Use Fibonacci ratios to find repeating pattern
print("\n" + "="*60)
print("Method 4: Fibonacci ratio-based extraction")
print("="*60)

phi = (1 + np.sqrt(5)) / 2  # Golden ratio

bits = []
for i in range(20000):
    # Use golden ratio to determine sampling positions
    radius = (i / phi) % 1000 + 100  # Wrap around
    angle = i * 2 * np.pi / phi
    
    x = int(center_x + radius * np.cos(angle))
    y = int(center_y + radius * np.sin(angle))
    
    if 0 <= x < w and 0 <= y < h:
        bits.append(red[y, x] & 1)
        if len(bits) >= 10000:
            break

print(f"Extracted {len(bits)} bits using golden ratio")

if len(bits) >= 80:
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    print(f"Sample: {text[:200]}")
    
    if 'flag{' in text.lower():
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"\n[+] FLAG: {flag}\n")
            with open('FLAG.txt', 'w') as f:
                f.write(flag)

print("\nDone analyzing fractal patterns")
