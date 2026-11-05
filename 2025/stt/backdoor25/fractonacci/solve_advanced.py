#!/usr/bin/env python3
"""
Fractonacci CTF Challenge Solver - Advanced
Tries multiple LSB extraction methods including Fibonacci patterns
"""

from PIL import Image
import sys

def fibonacci_sequence(n):
    """Generate first n Fibonacci numbers"""
    fib = [0, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib

def extract_red_lsb_fibonacci(image_path):
    """Extract LSB from red channel using Fibonacci sequence positions"""
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    total_pixels = width * height
    
    print(f"Image size: {width}x{height} = {total_pixels} pixels")
    
    # Try reading in Fibonacci sequence order
    fib_positions = fibonacci_sequence(min(total_pixels, 1000))
    bits = []
    
    for pos in fib_positions:
        if pos >= total_pixels:
            break
        x = pos % width
        y = pos // width
        pixel = pixels[x, y]
        if isinstance(pixel, tuple):
            r = pixel[0]
        else:
            r = pixel
        bits.append(r & 1)
    
    # Convert to bytes
    bytes_data = []
    for i in range(0, len(bits) - 7, 8):
        byte_bits = bits[i:i+8]
        byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
        bytes_data.append(byte_val)
    
    result = bytes(bytes_data)
    print("\n[Fibonacci order] Decoded bytes:")
    print(result[:200])
    try:
        text = result.decode('ascii', errors='ignore')
        print(text[:500])
        if 'flag' in text.lower():
            print(f"\n[+] Possible flag found: {text}")
    except:
        pass
    
    return result

def extract_red_lsb_sequential(image_path):
    """Extract LSB from red channel sequentially"""
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    bits = []
    
    # Extract LSB from red channel
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if isinstance(pixel, tuple):
                r = pixel[0]
            else:
                r = pixel
            bits.append(r & 1)
    
    # Convert to bytes
    bytes_data = []
    for i in range(0, len(bits) - 7, 8):
        byte_bits = bits[i:i+8]
        byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
        bytes_data.append(byte_val)
    
    result = bytes(bytes_data)
    print("\n[Sequential order] First 200 bytes:")
    print(result[:200])
    
    # Look for flag pattern
    text = result.decode('ascii', errors='ignore')
    
    # Search for common flag formats
    for pattern in ['flag{', 'FLAG{', 'ctf{', 'CTF{', 'backdoor{']:
        if pattern in text:
            start = text.find(pattern)
            end = text.find('}', start)
            if end != -1:
                flag = text[start:end+1]
                print(f"\n[+] Found flag: {flag}")
                return flag
    
    # Save full extraction
    with open('extracted_sequential.txt', 'wb') as f:
        f.write(result)
    print("Saved to extracted_sequential.txt")
    
    return result

def extract_red_lsb_reverse_bits(image_path):
    """Extract LSB but reverse bit order in bytes"""
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size
    
    bits = []
    
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if isinstance(pixel, tuple):
                r = pixel[0]
            else:
                r = pixel
            bits.append(r & 1)
    
    # Convert to bytes with reversed bit order
    bytes_data = []
    for i in range(0, len(bits) - 7, 8):
        byte_bits = bits[i:i+8]
        byte_val = sum(bit << j for j, bit in enumerate(byte_bits))  # Reversed
        bytes_data.append(byte_val)
    
    result = bytes(bytes_data)
    print("\n[Reversed bits] First 200 bytes:")
    print(result[:200])
    
    text = result.decode('ascii', errors='ignore')
    if 'flag' in text.lower():
        print(f"\n[+] Possible flag: {text[:200]}")
    
    return result

def main():
    image_path = sys.argv[1] if len(sys.argv) > 1 else 'challenge.png'
    
    print(f"[*] Analyzing: {image_path}\n")
    
    # Try different extraction methods
    print("="*60)
    print("Method 1: Sequential LSB extraction")
    print("="*60)
    extract_red_lsb_sequential(image_path)
    
    print("\n" + "="*60)
    print("Method 2: Fibonacci sequence positions")
    print("="*60)
    extract_red_lsb_fibonacci(image_path)
    
    print("\n" + "="*60)
    print("Method 3: Reversed bit order")
    print("="*60)
    extract_red_lsb_reverse_bits(image_path)

if __name__ == "__main__":
    main()
