#!/usr/bin/env python3
"""
Quick check of LSB image for text patterns
"""

from PIL import Image
import numpy as np

# Load the LSB visualization
img = Image.open('red_lsb.png')
img_array = np.array(img)

print(f"Image shape: {img_array.shape}")
print(f"Unique values: {np.unique(img_array)}")

# Check a middle region
h, w = img_array.shape[:2]
region = img_array[h//4:h//4+100, w//4:w//4+100]
print(f"\nSample region:")
print(region[:20, :20])

# Count black vs white pixels
if len(img_array.shape) == 2:
    black = np.sum(img_array == 0)
    white = np.sum(img_array == 255)
else:
    black = np.sum(img_array[:,:,0] == 0)
    white = np.sum(img_array[:,:,0] == 255)

total = h * w
print(f"\nPixel distribution:")
print(f"  Black (0): {black} ({black/total*100:.2f}%)")
print(f"  White (255): {white} ({white/total*100:.2f}%)")

# The image might contain a QR code or text
# Let's try to detect if there are any structured patterns
print("\nTrying to find patterns...")

# Sample some rows to see if there's structure
for y in [h//4, h//2, 3*h//4]:
    row = img_array[y, :]
    if len(img_array.shape) == 3:
        row = row[:, 0]
    # Look for transitions
    transitions = np.sum(np.diff(row) != 0)
    print(f"Row {y}: {transitions} transitions")
