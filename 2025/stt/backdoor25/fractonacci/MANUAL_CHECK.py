#!/usr/bin/env python3
"""
Create a summary document listing all files to check manually
"""

print("""
FRACTONACCI CTF CHALLENGE - MANUAL CHECK REQUIRED
================================================

The LSB has been extracted and visualized. The flag is likely VISIBLE in one of these images.

FILES TO CHECK VISUALLY:
-----------------------

1. MAIN LSB VISUALIZATIONS:
   - red_lsb_small.png (2000x2000 - easier to view)
   - red_lsb.png (6000x6000 - full resolution)
   - lsb_large_center.png (central 2000x2000 region)

2. ENHANCED VERSIONS:
   - lsb_threshold_200.png (high threshold)
   - lsb_threshold_150.png
   - lsb_threshold_100.png  
   - lsb_threshold_50.png (low threshold)
   - lsb_edges.png (edge detection)
   - red_lsb_inverted.png (inverted colors)

3. INTERESTING REGIONS (high variance = likely text):
   - interesting_tile_0_4500_0.png
   - interesting_tile_1_2500_2500.png (CENTRAL REGION - CHECK THIS!)
   - interesting_tile_2_2500_3000.png (CENTRAL REGION - CHECK THIS!)
   - interesting_tile_3_3000_3000.png (CENTRAL REGION - CHECK THIS!)
   - interesting_tile_4_3000_2500.png (CENTRAL REGION - CHECK THIS!)
   - montage_tiles.png (all tiles in one view)

4. BIT PLANES:
   - red_bit0.png through red_bit7.png
   - green_lsb.png, blue_lsb.png

HOW TO VIEW:
-----------

Option 1: Use image viewer
    eog red_lsb_small.png
    # or
    display red_lsb_small.png
    # or
    gimp red_lsb.png

Option 2: Convert to different format
    convert red_lsb.png -resize 1000x1000 -enhance output.jpg

Option 3: Look for patterns
    The flag format is: flag{...}
    Look for letters formed by white pixels on black background
    Or black letters on white background in inverted version

KEY FINDINGS:
------------
- LSB distribution: 88% black, 12% white (NON-RANDOM = hidden data!)
- Very dense center at (2800, 2800) with 97.9% white pixels
- The fractal pattern suggests visual encoding
- "Fractonacci" = Fractal + Fibonacci hints at the method

The flag is VISUAL - embedded in the image pattern!
Look at the central region tiles especially.
""")

# Also create a script to view all images in sequence
with open('view_all.sh', 'w') as f:
    f.write("""#!/bin/bash
# View all important images
echo "Opening LSB visualizations..."
eog red_lsb_small.png &
sleep 2
eog interesting_tile_1_2500_2500.png &
sleep 2  
eog interesting_tile_2_2500_3000.png &
sleep 2
eog montage_tiles.png &
echo "Check the opened images for the flag!"
""")

import os
os.chmod('view_all.sh', 0o755)
print("\nCreated view_all.sh - run it to open all important images")
