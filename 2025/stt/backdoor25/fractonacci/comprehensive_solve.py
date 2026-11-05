#!/usr/bin/env python3
"""
Final comprehensive attempt - try all reasonable approaches
"""

from PIL import Image
import numpy as np

def fib_sequence(max_n):
    """Generate Fibonacci sequence up to max_n"""
    fibs = [0, 1]
    while fibs[-1] < max_n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs

def try_all_bit_planes():
    """Extract and analyze all 8 bit planes from all RGB channels"""
    img = Image.open('challenge.png')
    img_array = np.array(img)
    
    results = []
    
    for channel_idx, channel_name in enumerate(['R', 'G', 'B']):
        channel = img_array[:, :, channel_idx]
        
        for bit_pos in range(8):
            bits = []
            height, width = channel.shape
            
            # Extract this bit plane
            for y in range(height):
                for x in range(width):
                    bits.append((channel[y, x] >> bit_pos) & 1)
            
            # Convert to bytes
            bytes_data = []
            for i in range(0, min(len(bits), 800000), 8):  # First 100KB
                if i + 8 <= len(bits):
                    byte_bits = bits[i:i+8]
                    byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
                    bytes_data.append(byte_val)
            
            result = bytes(bytes_data)
            
            # Check for flag
            text = result.decode('ascii', errors='ignore')
            
            # Look for flag patterns
            for pattern in ['flag{', 'backdoor{', 'FLAG{', 'BACKDOOR{', 'ctf{', 'CTF{']:
                if pattern in text:
                    idx = text.find(pattern)
                    end_idx = text.find('}', idx)
                    if end_idx != -1:
                        flag = text[idx:end_idx+1]
                        print(f"\n{'='*60}")
                        print(f"[+] FOUND FLAG in {channel_name} channel, bit {bit_pos}!")
                        print(f"{'='*60}")
                        print(f"FLAG: {flag}")
                        print(f"{'='*60}\n")
                        results.append((channel_name, bit_pos, flag))
                        
                        # Save this extraction
                        with open(f'flag_found_{channel_name}_bit{bit_pos}.txt', 'wb') as f:
                            f.write(result)
                        return flag
            
            # Check readability
            printable = sum(1 for c in text[:500] if c.isprintable() and c not in '\x00\xff')
            if printable > 250:  # More than 50% printable
                print(f"{channel_name} bit {bit_pos}: {printable}/500 printable chars")
                print(f"  Sample: {text[:100]}")
                
                # Save promising ones
                with open(f'extract_{channel_name}_bit{bit_pos}.txt', 'wb') as f:
                    f.write(result[:10000])  # First 10KB
    
    return None

def main():
    print("Starting comprehensive bit plane analysis...")
    print("This will check all RGB channels and all 8 bit positions")
    print("="*60)
    
    flag = try_all_bit_planes()
    
    if flag:
        print(f"\n\n{'#'*60}")
        print(f"SUCCESS! Flag found: {flag}")
        print(f"{'#'*60}\n")
    else:
        print("\nNo flag found in standard bit plane extraction.")
        print("Check the generated extract_*.txt files for clues.")

if __name__ == "__main__":
    main()
