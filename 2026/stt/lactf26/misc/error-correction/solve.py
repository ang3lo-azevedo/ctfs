import numpy as np
from PIL import Image
from pyzbar.pyzbar import decode
import itertools
import sys

# 1. Load and process the image
try:
    img = Image.open('chall.png').convert('L')
except FileNotFoundError:
    print("Error: chall.png not found. Please provide the challenge image.")
    sys.exit(1)

# The original code resized 45x45 -> 450x450. We reverse this.
img = img.resize((45, 45), resample=Image.Resampling.NEAREST)
arr = np.array(img)

# 2. Extract the 25 blocks (9x9 each)
blocks = []
for y in range(5):
    for x in range(5):
        # The script extracted blocks by iterating rows then cols of blocks
        # We just need to grab every 9x9 chunk from the randomized image.
        # Wait, the challenge randomized the *list* of chunks.
        # So we just cut the scrambled image into 25 pieces again to get our "deck of cards".
        # The scrambled image was built row-by-row of blocks.
        r_start, r_end = y*9, (y+1)*9
        c_start, c_end = x*9, (x+1)*9
        block = arr[r_start:r_end, c_start:c_end]
        blocks.append(block)

# 3. Helper Functions for Feature Detection

def check_pattern(block, r_off, c_off, pattern, is_checklist=False):
    # pattern is list of lists of 1s (black) and 0s (white)
    # block is numpy array, 0=black, 255=white
    rows = len(pattern)
    cols = len(pattern[0])
    for r in range(rows):
        for c in range(cols):
            expected = pattern[r][c]
            try:
                val = block[r_off + r, c_off + c]
            except IndexError:
                return False
            
            if expected == 1 and val != 0: return False
            if expected == 0 and val != 255: return False
    return True

FINDER_PATTERN = [
    [1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,1,1,1,0,1],
    [1,0,0,0,0,0,1],
    [1,1,1,1,1,1,1]
]

ALIGNMENT_PATTERN = [
    [1,1,1,1,1],
    [1,0,0,0,1],
    [1,0,1,0,1],
    [1,0,0,0,1],
    [1,1,1,1,1]
]

def has_finder(block, corner):
    if corner == 'TL':
        return check_pattern(block, 0, 0, FINDER_PATTERN)
    if corner == 'TR':
        # TR finder is at top right of image, so top right of block (0,4)
        # Block is 9x9. Finder is 7x7. X range 2..8
        return check_pattern(block, 0, 2, FINDER_PATTERN)
    if corner == 'BL':
        # BL finder is bottom left of image. Y range 2..8
        return check_pattern(block, 2, 0, FINDER_PATTERN)
    return False

def has_alignment(block, local_y, local_x):
    # local_y, local_x are CENTERS.
    # Pattern is 5x5, so extends -2 to +2.
    # Top-Left of pattern is y-2, x-2.
    return check_pattern(block, local_y-2, local_x-2, ALIGNMENT_PATTERN)

def check_timing_h(block):
    # Expect Alternating L D L D ... (255, 0, 255, 0)
    # Starts ODD (9) -> Light
    row = block[6] # Row 6
    expected = [255, 0] * 5 # Enough for 9 pixels
    expected = expected[:9]
    for k in range(9):
        if row[k] != expected[k]: return False
    return True

def check_timing_v(block):
    # Expect Alternating L D L D ...
    col = block[:, 6] # Col 6
    expected = [255, 0] * 5
    expected = expected[:9]
    for k in range(9):
        if col[k] != expected[k]: return False
    return True

# 4. Identify Fixed Blocks
grid = [[None]*5 for _ in range(5)]
used_indices = set()

# Find Corners
print("Searching for Finders...")
for i, b in enumerate(blocks):
    if i in used_indices: continue
    if has_finder(b, 'TL'):
        if grid[0][0] is None:
            print(f"Assigning TL to index {i}")
            grid[0][0] = b
            used_indices.add(i)
        else:
            print(f"Warning: Duplicate TL candidate at {i}")
    elif has_finder(b, 'TR'):
        if grid[0][4] is None:
            print(f"Assigning TR to index {i}")
            grid[0][4] = b
            used_indices.add(i)
        else:
            print(f"Warning: Duplicate TR candidate at {i}")
    elif has_finder(b, 'BL'):
        if grid[4][0] is None:
            print(f"Assigning BL to index {i}")
            grid[4][0] = b
            used_indices.add(i)
        else:
            print(f"Warning: Duplicate BL candidate at {i}")

# Find Alignment Patterns
alignment_targets = [
    (2, 2, 4, 4), # Grid Y, Grid X, Local Y, Local X
    (4, 4, 2, 2),
    (0, 2, 6, 4),
    (2, 0, 4, 6),
    (2, 4, 4, 2),
    (4, 2, 2, 4)
]

print("Searching for Alignments...")
for gy, gx, ly, lx in alignment_targets:
    if grid[gy][gx] is not None: continue
    for i, b in enumerate(blocks):
        if i in used_indices: continue
        if has_alignment(b, ly, lx):
            print(f"Assigning Alignment ({gy},{gx}) to index {i}")
            grid[gy][gx] = b
            used_indices.add(i)
            break

# Fill (0,1) and (0,3)
print("Searching for Timing Horizontal...")
for x in [1, 3]:
    if grid[0][x] is None:
        for i, b in enumerate(blocks):
            if i in used_indices: continue
            if check_timing_h(b):
                print(f"Assigning TimingH (0,{x}) to index {i}")
                grid[0][x] = b
                used_indices.add(i)
                break

# Fill (1,0) and (3,0)
print("Searching for Timing Vertical...")
for y in [1, 3]:
    if grid[y][0] is None:
        for i, b in enumerate(blocks):
            if i in used_indices: continue
            if check_timing_v(b):
                print(f"Assigning TimingV ({y},0) to index {i}")
                grid[y][0] = b
                used_indices.add(i)
                break
                
print(f"Total blocks placed: {len(used_indices)}")


# 6. Determine the Correct Mask
import segno
print("Identifying Mask via structural blocks...")

confirmed_mask = None
dummy_qr_matrix = None

# We can check (0,0) TL Block.
# It contains Finder, Separator, and Format Information.
# Format Info depends on the mask.
# No data pixels should be in (0,0) for Version 7?
# Let's verify.
# Finder: (0,0) to (6,6)
# Separator: Row 7, Col 7.
# Format Info: Row 8 (cols 0..8), Col 8 (rows 0..8).
# Wait, Col 8 is in block (0,0) (Col idx 8 is in 0..8).
# So Block (0,0) is:
# Rows 0..8, Cols 0..8.
# All pixels in this 9x9 block are Function Patterns or Format Info.
# NONE are data.
# So Block (0,0) depends ONLY on the Mask.

for mask_id in range(8):
    # Dummy with any content, just need mask structure
    dummy = segno.make('A', error='L', version=7, mask=mask_id)
    
    # Convert dummy
    dm = np.zeros((45, 45), dtype=np.uint8)
    for r in range(45):
        for c in range(45):
            dm[r, c] = 0 if dummy.matrix[r][c] else 255
            
    # Check TL block
    target_tl = dm[0:9, 0:9]
    
    # We compare only the Format Information pixels, to avoid Timing/Separator issues
    # although those should match too.
    # Format bits coordinates in TL block:
    # Row 8: Cols 0,1,2,3,4,5, 7,8
    # Col 8: Rows 0,1,2,3,4,5, 7
    coords = [
        (8,0), (8,1), (8,2), (8,3), (8,4), (8,5), (8,7), (8,8),
        (7,8), (5,8), (4,8), (3,8), (2,8), (1,8), (0,8)
    ]
    
    match = True
    for r, c in coords:
        if grid[0][0][r, c] != target_tl[r, c]:
            match = False
            break
            
    if match:
        print(f"Mask {mask_id} matches Format Info!")
        confirmed_mask = mask_id
        dummy_qr_matrix = dm
        break

if confirmed_mask is None:
    print("Error: No mask matched the TL block. Check segregation logic.")
    sys.exit(1)

print(f"Confirmed Mask: {confirmed_mask}")

# 7. Brute Force Missing Blocks
# Now we know the mask.
# We also generated a dummy matrix `dummy_qr_matrix`.
# But this dummy matrix has 'A' as content.
# The `remaining_blocks` contain the flag data blocks.
# Some blocks (padding) might match our dummy if we get the length/parity right.
# But we can simpler brute force now.
# We have 12 remaining slots.
# We know the mask.
# Wait, brute forcing 12 blocks is 12! = 479,001,600. Too big.
# We need to pin more blocks.

# We can try to pin blocks that match 'lactf{' prefix?
# 'lactf{' is at the start of data.
# Data fills from Bottom-Right.
# Block (4,4) is Alignment (Structural). Fixed.
# Block (3,4) is Data.
# Block (2,4) is Alignment. Fixed.
# Block (1,4) is Data.
# Block (0,4) is Finder. Fixed.
# Block (4,3) is next strip...

# So the first few Data Blocks are (3,4), (1,4), (4,3), (3,3)...
# If we assume flag starts with "lactf{", we can generate a QR with that prefix
# and see which of our `remaining_blocks` match the expected pixels for (3,4), (1,4) etc.

prefixes = ["lactf{"]
good_matches = []

# Try multiple lengths to see which gives best padding matches too?
# Or just stick to the known prefix part.
# The prefix "lactf{" affects the beginning of the stream.
# So pixels corresponding to "lactf{" should match perfectly regardless of total length (mostly).
# Interleaved blocks? No, V7-L has blocks but "lactf{" is short enough to fit in first block.
# Actually V7-L has 1 block of data codewords?
# Let's check Segno/QR Version 7-L specs.
# Version 7-L: Total data codewords 154. Blocks: 1.
# So no interleaving. The bytes just flow linearly.
# So "lactf{" determines the first few bytes absolutely.
# So the pixels for these bytes are FIXED for a given mask.

# Let's generate a reference QR with "lactf{......"
# Length doesn't matter for the *start* of the stream.
ref_qr = segno.make('lactf{A}', error='L', version=7, mask=confirmed_mask, boost_error=False, mode='byte')
ref_matrix = np.zeros((45, 45), dtype=np.uint8)
for r in range(45):
    for c in range(45):
        ref_matrix[r, c] = 0 if ref_qr.matrix[r][c] else 255

# Identify which of our `remaining_blocks` correspond to (3,4) and (1,4)
# by comparing with `ref_matrix`.
matched_data_slots = {}
assignments = {}

potential_data_slots = [(3,4), (1,4), (4,3), (3,3)] # Early data slots

for y, x in potential_data_slots:
    if grid[y][x] is not None: continue
    
    target = ref_matrix[y*9:(y+1)*9, x*9:(x+1)*9]
    # Look for match in remaining blocks
    for idx_b in remaining_indices:
        if idx_b in assignments.values(): continue
        # Note: We must be careful. "lactf{" might not fill the whole block.
        # But (3,4) and (1,4) are early enough that they are likely fully determined by "lactf{...".
        # Let's try exact match.
        if np.array_equal(blocks[idx_b], target):
            print(f"Matched Data Block at ({y},{x}) with index {idx_b}")
            assignments[(y,x)] = idx_b
            matched_data_slots[(y,x)] = blocks[idx_b]
            break

# Also try to match Padding Blocks (Left side)
# We try 2 parities for length.
matched_padd_slots = {}
for parity in [0, 1]:
    d_pad = segno.make('A' * (1+parity), error='L', version=7, mask=confirmed_mask, boost_error=False, mode='byte')
    dm_pad = np.zeros((45, 45), dtype=np.uint8)
    for r in range(45):
        for c in range(45):
            dm_pad[r, c] = 0 if d_pad.matrix[r][c] else 255
            
    # Check left slots: (0,0), (1,0) etc... 
    # Actually just check ALL empty slots against remaining blocks
    # If we find a match, it's a padding block candidate.
    
    current_matches = {}
    for y, x in remaining_pos:
        if (y,x) in assignments: continue 
        target = dm_pad[y*9:(y+1)*9, x*9:(x+1)*9]
        for idx_b in remaining_indices:
            if idx_b in assignments.values(): continue
            if idx_b in current_matches.values(): continue
            
            if np.array_equal(blocks[idx_b], target):
                current_matches[(y,x)] = idx_b
                break
    
    if len(current_matches) > len(matched_padd_slots):
        matched_padd_slots = current_matches

print(f"Matched {len(assignments)} data blocks and {len(matched_padd_slots)} padding blocks.")

# Combine
final_assignments = {**assignments, **matched_padd_slots}

# Place them
temp_grid = [row[:] for row in grid]
assigned_indices = set(used_indices)
assigned_indices.update(final_assignments.values())

for (y,x), idx in final_assignments.items():
    temp_grid[y][x] = blocks[idx]

# Brute force rest
unfilled = [p for p in remaining_pos if p not in final_assignments]
unused = [blocks[i] for i in remaining_indices if i not in assigned_indices]

print(f"Brute forcing remaining {len(unfilled)} blocks...")

import itertools
for p in itertools.permutations(unused):
    c_grid = [r[:] for r in temp_grid]
    for i, (uy, ux) in enumerate(unfilled):
        c_grid[uy][ux] = p[i]
    
    full_img = np.zeros((45, 45), dtype=np.uint8)
    for r in range(5):
        for c in range(5):
            full_img[r*9:(r+1)*9, c*9:(c+1)*9] = c_grid[r][c]
    
    big_img = Image.fromarray(full_img).resize((450, 450), resample=Image.Resampling.NEAREST)
    decoded = decode(big_img)
    if decoded:
        print("SUCCESS!")
        print(f"Flag: {decoded[0].data.decode()}")
        sys.exit(0)

print("Failed to decode after brute force.")

