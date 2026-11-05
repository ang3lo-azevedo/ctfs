#!/usr/bin/env python3
"""
Fractonacci - Extract LSB from specific patterns/regions
Maybe the flag is encoded in the fractal structure itself
"""

from PIL import Image
import numpy as np

def analyze_image(image_path):
    """Analyze the image for patterns"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    print(f"Image shape: {img_array.shape}")
    print(f"Image dtype: {img_array.dtype}")
    print(f"Image mode: {img.mode}")
    
    # Check red channel statistics
    if len(img_array.shape) == 3:
        red_channel = img_array[:, :, 0]
    else:
        red_channel = img_array
    
    print(f"\nRed channel stats:")
    print(f"  Min: {red_channel.min()}")
    print(f"  Max: {red_channel.max()}")
    print(f"  Mean: {red_channel.mean():.2f}")
    
    # Check LSB distribution
    lsb = red_channel & 1
    ones = np.sum(lsb == 1)
    zeros = np.sum(lsb == 0)
    print(f"\nLSB distribution:")
    print(f"  Ones: {ones} ({ones/(ones+zeros)*100:.2f}%)")
    print(f"  Zeros: {zeros} ({zeros/(ones+zeros)*100:.2f}%)")
    
    # If LSB is not ~50/50, might indicate hidden data
    if not (0.48 < ones/(ones+zeros) < 0.52):
        print("  -> LSB distribution is NOT random! Likely contains data")
    
    return img, img_array, red_channel

def extract_from_white_regions(image_path):
    """Extract LSB only from white/bright flower regions"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        red = img_array[:, :, 0]
        green = img_array[:, :, 1]
        blue = img_array[:, :, 2]
        
        # Find bright/white regions (flowers)
        brightness = (red.astype(int) + green.astype(int) + blue.astype(int)) / 3
        white_mask = brightness > 200  # Threshold for white regions
        
        print(f"White pixels: {np.sum(white_mask)}")
        
        # Extract LSB from white regions only
        bits = []
        height, width = red.shape
        for y in range(height):
            for x in range(width):
                if white_mask[y, x]:
                    bits.append(red[y, x] & 1)
        
        print(f"Extracted {len(bits)} bits from white regions")
        
        # Convert to bytes
        bytes_data = []
        for i in range(0, len(bits) - 7, 8):
            byte_bits = bits[i:i+8]
            byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
            bytes_data.append(byte_val)
        
        result = bytes(bytes_data)
        print(f"First 200 bytes from white regions:")
        print(result[:200])
        
        text = result.decode('ascii', errors='ignore')
        if 'flag' in text.lower() or 'backdoor' in text.lower():
            print(f"\n[+] Found in text: {text[:500]}")
        
        with open('extracted_white.txt', 'wb') as f:
            f.write(result)

def extract_from_center(image_path):
    """Extract from center flower"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        red = img_array[:, :, 0]
    else:
        red = img_array
    
    height, width = red.shape
    center_x, center_y = width // 2, height // 2
    
    # Extract in spiral from center
    bits = []
    radius = 1
    max_radius = min(width, height) // 2
    
    while radius < max_radius:
        # Extract from circle at this radius
        for angle in range(0, 360, 1):
            x = int(center_x + radius * np.cos(np.radians(angle)))
            y = int(center_y + radius * np.sin(np.radians(angle)))
            if 0 <= x < width and 0 <= y < height:
                bits.append(red[y, x] & 1)
        radius += 1
        
        if len(bits) > 100000:  # Limit
            break
    
    print(f"Extracted {len(bits)} bits from spiral")
    
    # Convert to bytes
    bytes_data = []
    for i in range(0, len(bits) - 7, 8):
        byte_bits = bits[i:i+8]
        byte_val = sum(bit << (7 - j) for j, bit in enumerate(byte_bits))
        bytes_data.append(byte_val)
    
    result = bytes(bytes_data)
    print(f"First 200 bytes from spiral:")
    print(result[:200])
    
    text = result.decode('ascii', errors='ignore')
    print(text[:500])

def main():
    image_path = 'challenge.png'
    
    print("="*60)
    print("Image Analysis")
    print("="*60)
    img, img_array, red_channel = analyze_image(image_path)
    
    print("\n" + "="*60)
    print("Method: Extract from white/bright regions")
    print("="*60)
    extract_from_white_regions(image_path)
    
    print("\n" + "="*60)
    print("Method: Extract in spiral from center")
    print("="*60)
    extract_from_center(image_path)

if __name__ == "__main__":
    main()
