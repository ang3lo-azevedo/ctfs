#!/usr/bin/env python3
"""
Fractonacci - Extract LSB from DARK regions (background)
Since white regions have all 1s in LSB, the data must be in the dark background
"""

from PIL import Image
import numpy as np

def extract_from_dark_regions(image_path):
    """Extract LSB only from dark/red background regions"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        red = img_array[:, :, 0]
        green = img_array[:, :, 1]
        blue = img_array[:, :, 2]
        
        # Find dark regions (background)
        brightness = (red.astype(int) + green.astype(int) + blue.astype(int)) / 3
        dark_mask = brightness < 200  # Threshold for dark regions
        
        print(f"Dark pixels: {np.sum(dark_mask)}")
        
        # Extract LSB from dark regions only
        bits = []
        height, width = red.shape
        for y in range(height):
            for x in range(width):
                if dark_mask[y, x]:
                    bits.append(red[y, x] & 1)
        
        print(f"Extracted {len(bits)} bits from dark regions")
        print(f"That's {len(bits)//8} bytes")
        
        # Convert to bytes
        bytes_data = []
        for i in range(0, len(bits) - 7, 8):
            byte_bits = bits[i:i+8]
            byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
            bytes_data.append(byte_val)
        
        result = bytes(bytes_data)
        
        # Save to file
        with open('extracted_dark.bin', 'wb') as f:
            f.write(result)
        print("Saved to extracted_dark.bin")
        
        # Try to decode as text
        text = result.decode('ascii', errors='ignore')
        
        # Print first part
        print(f"\nFirst 500 characters:")
        print(text[:500])
        
        # Look for flag
        for pattern in ['flag{', 'FLAG{', 'backdoor{', 'BACKDOOR{', 'ctf{', 'CTF{']:
            if pattern in text:
                start = text.find(pattern)
                end = text.find('}', start)
                if end != -1:
                    flag = text[start:end+1]
                    print(f"\n[+] FOUND FLAG: {flag}")
                    return flag
        
        # Search in full text
        if 'flag' in text.lower():
            idx = text.lower().find('flag')
            print(f"\n'flag' found at position {idx}:")
            print(text[max(0, idx-50):idx+100])
        
        return result

def extract_with_different_thresholds(image_path):
    """Try different brightness thresholds"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    red = img_array[:, :, 0]
    green = img_array[:, :, 1]
    blue = img_array[:, :, 2]
    brightness = (red.astype(int) + green.astype(int) + blue.astype(int)) / 3
    
    for threshold in [150, 175, 200, 225]:
        print(f"\n{'='*60}")
        print(f"Threshold: {threshold}")
        print(f"{'='*60}")
        
        dark_mask = brightness < threshold
        pixel_count = np.sum(dark_mask)
        print(f"Pixels selected: {pixel_count}")
        
        if pixel_count > 0:
            bits = []
            height, width = red.shape
            for y in range(height):
                for x in range(width):
                    if dark_mask[y, x]:
                        bits.append(red[y, x] & 1)
            
            bytes_data = []
            for i in range(0, len(bits) - 7, 8):
                byte_bits = bits[i:i+8]
                byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
                bytes_data.append(byte_val)
            
            result = bytes(bytes_data)
            text = result.decode('ascii', errors='ignore')
            
            print(f"First 200 chars: {text[:200]}")
            
            if 'flag' in text.lower() or 'backdoor' in text.lower():
                print(f"\n[+] POTENTIAL FLAG FOUND!")
                print(text[:1000])

def main():
    image_path = 'challenge.png'
    
    print("="*60)
    print("Extracting from DARK regions (background)")
    print("="*60)
    extract_from_dark_regions(image_path)
    
    print("\n\n")
    print("="*60)
    print("Trying different brightness thresholds")
    print("="*60)
    extract_with_different_thresholds(image_path)

if __name__ == "__main__":
    main()
