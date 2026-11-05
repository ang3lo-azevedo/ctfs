#!/usr/bin/env python3
"""
Check center region of LSB image for flag text
"""

from PIL import Image, ImageEnhance
import numpy as np

# Load LSB image
img = Image.open('red_lsb.png')
img_array = np.array(img)

h, w = img_array.shape
print(f"Full image: {w}x{h}")

# Extract center region
center_size = 1000
start_y = (h - center_size) // 2
start_x = (w - center_size) // 2
center = img_array[start_y:start_y+center_size, start_x:start_x+center_size]

# Save center region
center_img = Image.fromarray(center)
center_img.save('lsb_center.png')
print(f"Saved center region to lsb_center.png")

# Also try different regions
regions = [
    ("top_left", 0, 0, 1000, 1000),
    ("top_right", w-1000, 0, w, 1000),
    ("bottom_left", 0, h-1000, 1000, h),
    ("bottom_right", w-1000, h-1000, w, h),
]

for name, x1, y1, x2, y2 in regions:
    region = img_array[y1:y2, x1:x2]
    region_img = Image.fromarray(region)
    region_img.save(f'lsb_{name}.png')
    print(f"Saved {name} region")

# Try OCR on center
try:
    import pytesseract
    text = pytesseract.image_to_string(center_img)
    print(f"\nOCR result from center:")
    print(text[:500])
    if 'flag' in text.lower() or 'backdoor' in text.lower():
        print(f"\n[+] FLAG FOUND: {text}")
except ImportError:
    print("\npytesseract not available, skipping OCR")
except Exception as e:
    print(f"\nOCR error: {e}")

# Check if there are any dense clusters of white pixels
white_pixels = np.where(img_array == 255)
if len(white_pixels[0]) > 0:
    min_y, max_y = white_pixels[0].min(), white_pixels[0].max()
    min_x, max_x = white_pixels[1].min(), white_pixels[1].max()
    print(f"\nWhite pixel bounding box: ({min_x}, {min_y}) to ({max_x}, {max_y})")
    print(f"Size: {max_x-min_x}x{max_y-min_y}")
    
    # Extract that region
    bbox_region = img_array[min_y:max_y, min_x:max_x]
    bbox_img = Image.fromarray(bbox_region)
    bbox_img.save('lsb_bbox.png')
    print("Saved bounding box region to lsb_bbox.png")
