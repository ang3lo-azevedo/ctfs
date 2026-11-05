#!/usr/bin/env python3
"""
Final attempt - check if flag is encoded as pixel coordinates
or try reading the fractal in a spiral/Fibonacci pattern
"""
from PIL import Image
import numpy as np

img = Image.open('challenge.png')
arr = np.array(img)
red = arr[:, :, 0]
h, w = red.shape

# Try Fibonacci spiral reading
def fib_gen():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

print("="*60)
print("Method: Fibonacci spiral from center")
print("="*60)

center_x, center_y = w // 2, h // 2
fibs = []
fib_iter = fib_gen()
for _ in range(30):
    fibs.append(next(fib_iter))

bits = []
for radius_idx, radius in enumerate(fibs[2:20]):  # Skip 0 and 1
    # Sample points at this Fibonacci radius
    angles = np.linspace(0, 2*np.pi, radius * 8 + 1)[:-1]
    for angle in angles:
        x = int(center_x + radius * np.cos(angle))
        y = int(center_y + radius * np.sin(angle))
        if 0 <= x < w and 0 <= y < h:
            bits.append(red[y, x] & 1)

if len(bits) > 80:
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
            print(f"\n[+] FLAG: {text[idx:end+1]}\n")

# Try reading only from specific flower petals (bright spots)
print("\n" + "="*60)
print("Method: Extract from brightest pixels only")
print("="*60)

# Find brightest pixels
brightness = arr[:, :, :3].mean(axis=2)
threshold = np.percentile(brightness, 99)  # Top 1% brightest
bright_mask = brightness > threshold

# Get coordinates of bright pixels, sorted
bright_coords = np.argwhere(bright_mask)
# Sort by distance from center
distances = np.sqrt((bright_coords[:, 0] - center_y)**2 + (bright_coords[:, 1] - center_x)**2)
sorted_idx = np.argsort(distances)
bright_coords_sorted = bright_coords[sorted_idx]

bits = []
for coord in bright_coords_sorted[:10000]:  # First 10000 bright pixels
    y, x = coord
    bits.append(red[y, x] & 1)

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
        print(f"\n[+] FLAG: {text[idx:end+1]}\n")

# One more try - maybe bits need to be reversed within each byte
print("\n" + "="*60)
print("Method: Reversed bit order in each byte")
print("="*60)

bits = []
for y in range(min(1000, h)):
    for x in range(min(1000, w)):
        bits.append(red[y, x] & 1)

bytes_data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte_bits = bits[i:i+8]
    byte_val = sum(byte_bits[j] << j for j in range(8))  # Reversed
    bytes_data.append(byte_val)

text = bytes_data.decode('ascii', errors='ignore')
print(f"Sample: {text[:200]}")

if 'flag{' in text.lower():
    idx = text.lower().find('flag{')
    end = text.find('}', idx)
    if end > idx:
        print(f"\n[+] FLAG: {text[idx:end+1]}\n")

print("\nChecked Fibonacci spiral, bright pixels, and reversed bits")
