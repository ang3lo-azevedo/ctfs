#!/usr/bin/env python3
"""
Try reading bits in different byte orders and with different bit plane combinations
"""
from PIL import Image
import numpy as np

img = Image.open('challenge.png')
arr = np.array(img)

# Method 1: Try LSB from all channels combined
print("="*60)
print("Method 1: Combining LSB from RGB channels")
print("="*60)

bits = []
for y in range(min(2000, arr.shape[0])):
    for x in range(min(2000, arr.shape[1])):
        r, g, b = arr[y, x, :3]
        bits.append(r & 1)
        bits.append(g & 1)
        bits.append(b & 1)
        if len(bits) >= 200000:
            break
    if len(bits) >= 200000:
        break

bytes_data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte_val = sum(bits[i+j] << (7-j) for j in range(8))
    bytes_data.append(byte_val)

text = bytes_data.decode('ascii', errors='ignore')
if 'flag{' in text.lower():
    idx = text.lower().find('flag{')
    end = text.find('}', idx)
    if end > idx:
        print(f"\n[+] FLAG: {text[idx:end+1]}\n")

print(f"Sample: {text[:100]}")

# Method 2: Try bit plane 1 (second LSB)
print("\n" + "="*60)
print("Method 2: Second LSB (bit 1)")
print("="*60)

bits = []
red = arr[:, :, 0]
for y in range(min(2000, red.shape[0])):
    for x in range(min(2000, red.shape[1])):
        bits.append((red[y, x] >> 1) & 1)

bytes_data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte_val = sum(bits[i+j] << (7-j) for j in range(8))
    bytes_data.append(byte_val)

text = bytes_data.decode('ascii', errors='ignore')
if 'flag{' in text.lower():
    idx = text.lower().find('flag{')
    end = text.find('}', idx)
    if end > idx:
        print(f"\n[+] FLAG: {text[idx:end+1]}\n")

print(f"Sample: {text[:100]}")

# Method 3: XOR of multiple channels' LSB
print("\n" + "="*60)
print("Method 3: XOR of R, G, B LSBs")
print("="*60)

bits = []
for y in range(min(2000, arr.shape[0])):
    for x in range(min(2000, arr.shape[1])):
        r, g, b = arr[y, x, :3]
        bit = (r & 1) ^ (g & 1) ^ (b & 1)
        bits.append(bit)

bytes_data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte_val = sum(bits[i+j] << (7-j) for j in range(8))
    bytes_data.append(byte_val)

text = bytes_data.decode('ascii', errors='ignore')
if 'flag{' in text.lower():
    idx = text.lower().find('flag{')
    end = text.find('}', idx)
    if end > idx:
        print(f"\n[+] FLAG: {text[idx:end+1]}\n")

print(f"Sample: {text[:100]}")

# Method 4: Try reading from alpha channel
print("\n" + "="*60)
print("Method 4: Alpha channel LSB")
print("="*60)

if arr.shape[2] == 4:
    bits = []
    alpha = arr[:, :, 3]
    for y in range(min(2000, alpha.shape[0])):
        for x in range(min(2000, alpha.shape[1])):
            bits.append(alpha[y, x] & 1)
    
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    if 'flag{' in text.lower():
        idx = text.lower().find('flag{')
        end = text.find('}', idx)
        if end > idx:
            print(f"\n[+] FLAG: {text[idx:end+1]}\n")
    
    print(f"Sample: {text[:100]}")
else:
    print("No alpha channel")

print("\nDone checking alternative methods")
