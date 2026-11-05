#!/usr/bin/env python3
from PIL import Image

img = Image.open('challenge.png')
w, h = img.size

print("Extracting Green channel LSB (full image)...")
bits = []

for y in range(h):
    for x in range(w):
        pixel = img.getpixel((x, y))
        bits.append(pixel[1] & 1)  # Green channel
    if y % 1000 == 0:
        print(f"Progress: {y}/{h} rows")

print(f"Total bits: {len(bits)}")

# Convert to bytes
bytes_data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte_val = sum(bits[i+j] << (7-j) for j in range(8))
    bytes_data.append(byte_val)

print(f"Total bytes: {len(bytes_data)}")

# Save full extraction
with open('green_lsb_full.bin', 'wb') as f:
    f.write(bytes_data)

# Search for flag in full data
text = bytes_data.decode('ascii', errors='ignore')

for pattern in ['flag{', 'backdoor{', 'FLAG{', 'BACKDOOR{', 'ctf{', 'CTF{']:
    if pattern in text:
        idx = text.find(pattern)
        end = text.find('}', idx)
        if end > idx:
            flag = text[idx:end+1]
            print(f"\n[+] FOUND FLAG: {flag}\n")
            with open('FLAG.txt', 'w') as f:
                f.write(flag)

# Also search in lowercase
lower_text = text.lower()
if 'flag' in lower_text:
    idx = lower_text.find('flag')
    print(f"\nFound 'flag' at position {idx}:")
    print(f"Context: {text[max(0, idx-50):idx+150]}")

# Check if there are strings
import re
strings = re.findall(r'[ -~]{10,}', text)
if strings:
    print(f"\nFound {len(strings)} readable strings, showing first 20:")
    for s in strings[:20]:
        print(f"  {s}")
