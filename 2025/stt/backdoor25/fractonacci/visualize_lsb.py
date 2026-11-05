#!/usr/bin/env python3
"""
Fractonacci - Reconstruct image from LSB data
The LSB data might form an image itself
"""

from PIL import Image
import numpy as np

def reconstruct_image_from_lsb(image_path):
    """Extract LSB and try to form new image"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        red = img_array[:, :, 0]
    else:
        red = img_array
    
    height, width = red.shape
    
    # Extract LSB
    lsb_array = (red & 1) * 255  # Convert 0/1 to 0/255
    
    # Save as image
    lsb_img = Image.fromarray(lsb_array.astype(np.uint8))
    lsb_img.save('lsb_visualization.png')
    print("Saved LSB visualization to lsb_visualization.png")
    
    return lsb_array

def extract_and_visualize_bits(image_path):
    """Extract LSB bits and display statistics"""
    img = Image.open(image_path)
    img_array = np.array(img)
    
    red = img_array[:, :, 0]
    green = img_array[:, :, 1]
    blue = img_array[:, :, 2]
    
    # Extract LSB from each channel
    red_lsb = (red & 1) * 255
    green_lsb = (green & 1) * 255
    blue_lsb = (blue & 1) * 255
    
    # Save individual channels
    Image.fromarray(red_lsb.astype(np.uint8)).save('red_lsb.png')
    Image.fromarray(green_lsb.astype(np.uint8)).save('green_lsb.png')
    Image.fromarray(blue_lsb.astype(np.uint8)).save('blue_lsb.png')
    
    print("Saved channel LSB visualizations:")
    print("  red_lsb.png")
    print("  green_lsb.png")
    print("  blue_lsb.png")
    
    # Also try combining
    combined = np.stack([red_lsb, green_lsb, blue_lsb], axis=2)
    Image.fromarray(combined.astype(np.uint8)).save('combined_lsb.png')
    print("  combined_lsb.png")

def extract_all_bits(image_path):
    """Extract all 8 bit planes from red channel"""
    img = Image.open(image_path)
    img_array = np.array(img)
    red = img_array[:, :, 0]
    
    for bit_pos in range(8):
        bit_plane = ((red >> bit_pos) & 1) * 255
        img_out = Image.fromarray(bit_plane.astype(np.uint8))
        img_out.save(f'red_bit{bit_pos}.png')
        print(f"Saved red_bit{bit_pos}.png (bit position {bit_pos})")

def main():
    image_path = 'challenge.png'
    
    print("="*60)
    print("Creating LSB visualization")
    print("="*60)
    reconstruct_image_from_lsb(image_path)
    
    print("\n" + "="*60)
    print("Extracting LSB from all RGB channels")
    print("="*60)
    extract_and_visualize_bits(image_path)
    
    print("\n" + "="*60)
    print("Extracting all bit planes from red channel")
    print("="*60)
    extract_all_bits(image_path)
    
    print("\n[*] Check the generated PNG files for hidden messages!")

if __name__ == "__main__":
    main()
