#!/usr/bin/env python3
from PIL import Image

img = Image.open('challenge.png')
w, h = img.size

for ch_name, ch_idx in [('R', 0), ('G', 1), ('B', 2)]:
    print(f"\nChecking {ch_name} channel LSB...")
    bits = []
    
    # Extract first 80000 bits (10KB)
    count = 0
    for y in range(h):
        for x in range(w):
            pixel = img.getpixel((x, y))
            bits.append(pixel[ch_idx] & 1)
            count += 1
            if count >= 80000:
                break
        if count >= 80000:
            break
    
    # Convert to bytes
    bytes_data = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = sum(bits[i+j] << (7-j) for j in range(8))
        bytes_data.append(byte_val)
    
    text = bytes_data.decode('ascii', errors='ignore')
    
    # Check for flag
    for pattern in ['flag{', 'backdoor{', 'FLAG{', 'BACKDOOR{']:
        if pattern in text:
            idx = text.find(pattern)
            end = text.find('}', idx)
            if end > idx:
                flag = text[idx:end+1]
                print(f"[+] FOUND: {flag}")
                with open(f'SOLUTION_{ch_name}.txt', 'w') as f:
                    f.write(flag)
    
    # Show sample
    printable = ''.join(c if c.isprintable() else '.' for c in text[:200])
    print(f"Sample: {printable[:100]}")
