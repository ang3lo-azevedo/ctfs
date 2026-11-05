#!/usr/bin/env python3
"""
Fractonacci - Extract using Fibonacci-based patterns
"""

from PIL import Image
import numpy as np

def fib(n):
    """Generate Fibonacci numbers up to n"""
    fibs = [1, 1]
    while fibs[-1] < n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

def extract_with_fib_grouping(image_path):
    """Group bits according to Fibonacci sequence"""
    img = Image.open(image_path)
    img_array = np.array(img)
    red = img_array[:, :, 0]
    
    # Get all LSB bits
    height, width = red.shape
    bits = []
    
    # Extract from dark regions only
    brightness = (img_array[:, :, 0].astype(int) + 
                  img_array[:, :, 1].astype(int) + 
                  img_array[:, :, 2].astype(int)) / 3
    dark_mask = brightness < 200
    
    for y in range(height):
        for x in range(width):
            if dark_mask[y, x]:
                bits.append(red[y, x] & 1)
    
    print(f"Total bits: {len(bits)}")
    
    # Try grouping by Fibonacci numbers
    fib_nums = fib(100)
    print(f"Fibonacci numbers to try: {fib_nums[:15]}")
    
    # Try reading N bits at a time where N is a Fibonacci number
    for fib_n in [1, 2, 3, 5, 8, 13, 21]:
        print(f"\n{'='*60}")
        print(f"Grouping by {fib_n} bits")
        print(f"{'='*60}")
        
        bytes_data = []
        i = 0
        while i + 8 <= len(bits):
            # Take 8 bits as usual
            byte_bits = bits[i:i+8]
            byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
            bytes_data.append(byte_val)
            i += fib_n  # Jump by Fibonacci number
        
        result = bytes(bytes_data[:1000])  # First 1000 bytes
        text = result.decode('ascii', errors='ignore')
        
        if any(c.isprintable() for c in text[:100]) and len([c for c in text[:100] if c.isprintable()]) > 50:
            print(f"Promising! First 200 chars:")
            print(text[:200])
            
            if 'flag' in text.lower() or 'backdoor' in text.lower():
                print(f"\n[+] FOUND FLAG PATTERN!")
                print(text[:500])

def extract_msb_not_lsb(image_path):
    """Try extracting MSB instead of LSB"""
    img = Image.open(image_path)
    img_array = np.array(img)
    red = img_array[:, :, 0]
    
    # Extract MSB (bit 7)
    height, width = red.shape
    bits = []
    
    brightness = (img_array[:, :, 0].astype(int) + 
                  img_array[:, :, 1].astype(int) + 
                  img_array[:, :, 2].astype(int)) / 3
    dark_mask = brightness < 200
    
    for y in range(height):
        for x in range(width):
            if dark_mask[y, x]:
                bits.append((red[y, x] >> 7) & 1)  # MSB
    
    print(f"\n{'='*60}")
    print(f"Extracting MSB (bit 7) instead of LSB")
    print(f"{'='*60}")
    
    # Convert to bytes
    bytes_data = []
    for i in range(0, len(bits) - 7, 8):
        byte_bits = bits[i:i+8]
        byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
        bytes_data.append(byte_val)
    
    result = bytes(bytes_data)
    text = result.decode('ascii', errors='ignore')
    print(f"First 200 chars:")
    print(text[:200])
    
    if 'flag' in text.lower():
        print(f"\n[+] FLAG FOUND in MSB!")
        print(text[:500])

def extract_bit_2(image_path):
    """Try extracting bit 2 (3rd bit)"""
    img = Image.open(image_path)
    img_array = np.array(img)
    red = img_array[:, :, 0]
    
    height, width = red.shape
    bits = []
    
    brightness = (img_array[:, :, 0].astype(int) + 
                  img_array[:, :, 1].astype(int) + 
                  img_array[:, :, 2].astype(int)) / 3
    dark_mask = brightness < 200
    
    for bit_pos in range(8):
        bits = []
        for y in range(height):
            for x in range(width):
                if dark_mask[y, x]:
                    bits.append((red[y, x] >> bit_pos) & 1)
        
        # Convert to bytes
        bytes_data = []
        for i in range(0, len(bits) - 7, 8):
            byte_bits = bits[i:i+8]
            byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
            bytes_data.append(byte_val)
        
        result = bytes(bytes_data)
        text = result.decode('ascii', errors='ignore')
        
        # Check if readable
        readable = sum(1 for c in text[:200] if c.isprintable())
        if readable > 100:
            print(f"\n{'='*60}")
            print(f"Bit position {bit_pos} looks readable!")
            print(f"{'='*60}")
            print(f"First 200 chars: {text[:200]}")
            
            if 'flag' in text.lower() or 'backdoor' in text.lower():
                print(f"\n[+] FLAG FOUND in bit position {bit_pos}!")
                # Search for full flag
                idx = text.lower().find('flag')
                if idx == -1:
                    idx = text.lower().find('backdoor')
                if idx >= 0:
                    print(text[idx:idx+100])

def main():
    image_path = 'challenge.png'
    
    extract_with_fib_grouping(image_path)
    extract_msb_not_lsb(image_path)
    extract_bit_2(image_path)

if __name__ == "__main__":
    main()
