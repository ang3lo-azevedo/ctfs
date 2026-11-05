#!/usr/bin/env python3
"""
Fractonacci CTF Challenge Solver
Extracts LSB from red channel of the image
"""

from PIL import Image
import sys

def extract_red_lsb(image_path):
    """Extract LSB from red channel of image"""
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    bits = []
    
    # Extract LSB from red channel of each pixel
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y][:3]  # Handle RGBA if present
            # Get least significant bit of red channel
            bits.append(r & 1)
    
    # Convert bits to bytes
    bytes_data = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_bits = bits[i:i+8]
            byte_val = 0
            for j, bit in enumerate(byte_bits):
                byte_val |= (bit << (7 - j))
            bytes_data.append(byte_val)
    
    # Convert to string and try to find flag
    try:
        result = bytes(bytes_data).decode('ascii', errors='ignore')
        print("Decoded text:")
        print(result[:1000])  # Print first 1000 chars
        
        # Look for flag format
        if 'flag{' in result.lower() or 'ctf{' in result.lower():
            start = result.lower().find('flag{')
            if start == -1:
                start = result.lower().find('ctf{')
            end = result.find('}', start)
            if end != -1:
                flag = result[start:end+1]
                print(f"\n[+] Found flag: {flag}")
        
    except Exception as e:
        print(f"Error decoding: {e}")
        # Try to save raw bytes
        with open('extracted_data.bin', 'wb') as f:
            f.write(bytes(bytes_data))
        print("Saved raw data to extracted_data.bin")

def main():
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = 'challenge.png'
    
    print(f"[*] Extracting LSB from red channel of: {image_path}")
    extract_red_lsb(image_path)

if __name__ == "__main__":
    main()
