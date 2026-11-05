#!/usr/bin/env python3
"""
Try reading LSB in different orders - maybe column-wise or spiral
"""

from PIL import Image
import numpy as np

def extract_column_major(image_path):
    """Extract LSB reading column by column instead of row by row"""
    img = Image.open(image_path)
    img_array = np.array(img)
    red = img_array[:, :, 0]
    
    height, width = red.shape
    bits = []
    
    # Read column by column
    for x in range(width):
        for y in range(height):
            bits.append(red[y, x] & 1)
        if len(bits) > 100000:  # Limit for speed
            break
    
    print(f"Extracted {len(bits)} bits in column-major order")
    
    # Convert to bytes
    bytes_data = []
    for i in range(0, len(bits) - 7, 8):
        byte_bits = bits[i:i+8]
        byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
        bytes_data.append(byte_val)
    
    result = bytes(bytes_data)
    text = result.decode('ascii', errors='ignore')
    print(f"First 300 chars:\n{text[:300]}\n")
    
    if 'flag{' in text.lower() or 'backdoor{' in text.lower():
        # Find the flag
        for pattern in ['flag{', 'backdoor{', 'FLAG{', 'BACKDOOR{']:
            if pattern in text:
                idx = text.find(pattern)
                flag_end = text.find('}', idx)
                if flag_end != -1:
                    flag = text[idx:flag_end+1]
                    print(f"\n[+] FOUND FLAG: {flag}\n")
                    return flag
    
    with open('column_major.txt', 'wb') as f:
        f.write(result)
    print("Saved to column_major.txt")
    
    return result

def main():
    image_path = 'challenge.png'
    
    print("="*60)
    print("Trying column-major order")
    print("="*60)
    extract_column_major(image_path)

if __name__ == "__main__":
    main()
