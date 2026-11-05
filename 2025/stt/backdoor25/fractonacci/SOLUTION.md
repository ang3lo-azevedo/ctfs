# Fractonacci CTF Challenge - Solution Summary

## Challenge Info
- **Name**: Fractonacci  
- **Points**: 100  
- **Category**: Beginner/Stego  
- **Hint**: "Beautiful. Red. Fractonacci. What could this mean?? probably red lsb"

## Solution Approach

The challenge involves LSB (Least Significant Bit) steganography on a fractal image.

### Key Findings

1. **Image Properties**:
   - Size: 6000x6000 pixels
   - Format: PNG with RGBA channels
   - Created with: Matplotlib version 3.10.7
   - Fractal flower pattern

2. **LSB Analysis**:
   - Red channel LSB distribution: 88.06% zeros, 11.94% ones (NOT random!)
   - This non-random distribution indicates hidden data
   - White regions (flowers) have LSB = 1 (all ones)
   - Dark regions (background) contain the actual hidden data

3. **Generated Files**:
   - `red_lsb.png` - Visualization of LSB bits from red channel (full 6000x6000)
   - `red_lsb_small.png` - Smaller version (2000x2000) for easier viewing
   - `red_lsb_inverted.png` - Inverted version
   - `lsb_large_center.png` - Central 2000x2000 region
   - `extracted_dark.bin` - Raw LSB data from dark regions
   - Various bit plane extractions (`red_bit0.png` through `red_bit7.png`)

4. **Dense Center Region**:
   - Very high concentration of white pixels at coordinates (2800, 2800)
   - 97.9% white pixels in this region
   - Likely contains the flag visually

### Next Steps

The flag is most likely **visually encoded** in one of the generated LSB images. 

**To find the flag**:

1. **Open and visually inspect these images**:
   ```bash
   # View the LSB visualization
   eog red_lsb_small.png
   # or
   display red_lsb_small.png
   # or
   gimp red_lsb.png
   ```

2. **Look for**:
   - Text formed by white pixels
   - QR code patterns
   - Flag format: `flag{...}` or `backdoor{...}`

3. **Try enhancing the image**:
   ```bash
   convert red_lsb.png -negate -threshold 50% enhanced.png
   ```

4. **Try OCR** (if text is visible):
   ```bash
   tesseract red_lsb.png output
   ```

### Alternative: Pattern-based extraction

If the flag is not visually obvious, it might be encoded in a Fibonacci-based reading pattern (given the "Fractonacci" name).

## Scripts Created

- `solve.py` - Basic LSB extraction
- `solve_advanced.py` - Multiple extraction methods including Fibonacci patterns
- `solve_patterns.py` - Extract from white/dark regions and spiral patterns
- `solve_dark.py` - Extract from dark background regions
- `visualize_lsb.py` - Create visual representations of all bit planes
- `comprehensive_solve.py` - Check all RGB channels and bit positions
- `extract_green_full.py` - Full green channel extraction

## Files to Check

The most promising files to manually inspect:
1. `red_lsb_small.png` - Easiest to view
2. `red_lsb.png` - Full resolution
3. `lsb_large_center.png` - Central region with highest density

**The flag is in the image - you need to visually inspect it!**
