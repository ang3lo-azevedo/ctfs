#!/usr/bin/env python3
"""
Extract LSB but only at Fibonacci sequence positions
Based on: https://github.com/klassiker/ctf-writeups/blob/master/2020/affinity-lite/forensics/fibonacci.md
"""
from PIL import Image

def fibonacci_sequence(max_val):
    """Generate Fibonacci sequence up to max_val"""
    fibs = [0, 1]
    while fibs[-1] + fibs[-2] < max_val:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

img = Image.open('challenge.png')
width, height = img.size
total_pixels = width * height

print(f"Image: {width}x{height} = {total_pixels} pixels")

# Generate Fibonacci positions
fib_positions = fibonacci_sequence(total_pixels)
print(f"Generated {len(fib_positions)} Fibonacci numbers")
print(f"First 20: {fib_positions[:20]}")
print(f"Last 5: {fib_positions[-5:]}")

# Extract LSB from red channel at Fibonacci positions
bits = []
for pos in fib_positions:
    if pos >= total_pixels:
        break
    
    # Convert position to x,y coordinates
    x = pos % width
    y = pos // width
    
    pixel = img.getpixel((x, y))
    r = pixel[0]
    
    # Get LSB
    bits.append(r & 1)

print(f"\nExtracted {len(bits)} bits from Fibonacci positions")
print(f"That's {len(bits) // 8} bytes")

# Convert bits to bytes
bytes_data = bytearray()
for i in range(0, len(bits) - 7, 8):
    byte_val = 0
    for j in range(8):
        byte_val |= (bits[i + j] << (7 - j))
    bytes_data.append(byte_val)

print(f"Converted to {len(bytes_data)} bytes")

# Try to decode as text
text = bytes_data.decode('ascii', errors='ignore')
print(f"\nFirst 500 characters:")
print(text[:500])

# Search for flag
for pattern in ['flag{', 'FLAG{', 'backdoor{', 'BACKDOOR{', 'ctf{', 'CTF{']:
    if pattern in text:
        idx = text.find(pattern)
        end_idx = text.find('}', idx)
        if end_idx > idx:
            flag = text[idx:end_idx+1]
            print(f"\n{'='*60}")
            print(f"[+] FOUND FLAG: {flag}")
            print(f"{'='*60}\n")
            
            with open('FLAG.txt', 'w') as f:
                f.write(flag)
            print("Saved to FLAG.txt")
            break
else:
    # Check if there's readable text with flag in it
    if 'flag' in text.lower():
        idx = text.lower().find('flag')
        print(f"\nFound 'flag' at position {idx}:")
        print(text[max(0, idx-50):idx+150])
    
    # Save full extraction
    with open('fibonacci_extraction.txt', 'wb') as f:
        f.write(bytes_data)
    print("\nSaved full extraction to fibonacci_extraction.txt")
    
    # Also try reversed bit order
    print("\n" + "="*60)
    print("Trying with reversed bit order...")
    print("="*60)
    
    bytes_data_rev = bytearray()
    for i in range(0, len(bits) - 7, 8):
        byte_val = 0
        for j in range(8):
            byte_val |= (bits[i + j] << j)  # Reversed
        bytes_data_rev.append(byte_val)
    
    text_rev = bytes_data_rev.decode('ascii', errors='ignore')
    print(f"First 200 chars: {text_rev[:200]}")
    
    for pattern in ['flag{', 'FLAG{', 'backdoor{', 'BACKDOOR{']:
        if pattern in text_rev:
            idx = text_rev.find(pattern)
            end_idx = text_rev.find('}', idx)
            if end_idx > idx:
                flag = text_rev[idx:end_idx+1]
                print(f"\n[+] FOUND FLAG (reversed): {flag}\n")
                with open('FLAG.txt', 'w') as f:
                    f.write(flag)
