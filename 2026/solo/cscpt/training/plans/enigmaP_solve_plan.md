# EnigmaP CTF Challenge - Solve Plan

## Challenge Overview

The binary `enigmaP` is an "oblivious" reversing challenge. It takes a difficulty level (0 or 1) and a 32-character flag as input. The flag format is `CSCPT{...}` (6 chars prefix + 25 chars content + 1 char `}` = 32 chars).

## Algorithm Analysis (Difficulty 1 - `sub_402f00`)

The difficulty 1 path is simpler and reveals the core algorithm directly. Both difficulty 0 and 1 perform the same mathematical transformation, but difficulty 0 uses ORAM (Oblivious RAM) to hide memory access patterns.

### Step 1: Byte-to-64bit packing
The 32-byte flag is packed into 4 x 64-bit integers. Each byte at positions `[i, i+8, i+16, i+24]` contributes to one 64-bit value through shift-and-OR operations. The packing interleaves bytes from different positions.

### Step 2: `sub_406270` - Bitonic Sort on Bit-Decomposed Values
This function:
1. **Bit decomposition**: Takes the 4 x 64-bit values (256 bits total) and creates 32 x 256-bit entries. Each entry represents one "bit position" - it shifts the data left by 8 bits repeatedly, creating 32 shifted copies (loop runs 0x1f = 31 times).
2. **NOT all bits**: XORs all entries with all-ones (`_mm256_cmpeq_epi32(zmm1, zmm1)` = all 0xFF).
3. **Bitonic sort** (`sub_405bc0`): Recursively sorts the 32 entries using a bitonic sorting network with direction=1.
4. **XOR with `0xFFFFFFFF00000000`**: XORs all entries with the pattern `-0x100000000` (upper 32 bits set).
5. **Bitonic sort again** with direction=1.
6. **XOR with `0x00000000FFFFFFFF`**: XORs all entries with lower 32 bits set.
7. **Bitonic sort again** with direction=1.
8. **Bit reassembly**: Extracts specific bytes from the sorted array at offsets `0x18, 0x118, 0x218, 0x318, 0x38, 0x138, 0x238, 0x338, ...` etc., masking with 0xFF and shifting to reconstruct 4 x 64-bit output values.

### Step 3: XOR with constant
The result is XORed with `data_420b20`:
```
89 ab cd ef 01 23 45 67 76 54 32 10 fe dc ba 98 85 ae 67 bb 67 e6 09 6a 3a f5 4f a5 72 f3 6e 3c
```
As 4 x 64-bit (little-endian):
- `0x67452301efcdab89`
- `0x98badcfe10325476`
- `0x6a09e667bb67ae85`
- `0x3c6ef372a54ff53a`

These are the SHA-256 initial hash values!

### Step 4: '@' character check
The XORed result is checked for `0x40` ('@') bytes. If any byte equals `0x40`, a flag `rdx_2` is set, and all bytes are zeroed out (making verification fail).

### Step 5: Second `sub_406270` call
The XORed (and potentially zeroed) result goes through `sub_406270` again.

### Step 6: Final comparison
The final 4 x 64-bit values are compared against:
```
var_50 == 0x6db9da380b5584c7
var_48 == 0x8a1840a1da251624  (from -0x75e7bf5e25dae9dc)
var_40 == 0x5e1cb4ac237ade56
var_38 == 0x141e12c1ecfd8efb
```

## Solving Strategy

Since `sub_406270` is a **deterministic sorting network** operating on 256-bit values, it's a bijection (invertible). The approach is:

1. **Reverse the second `sub_406270`**: Given the target output, reverse the bitonic sort to get the intermediate value.
2. **Reverse the XOR**: XOR with `data_420b20` to undo step 3.
3. **Reverse the first `sub_406270`**: Reverse the bitonic sort to get the original packed flag bytes.
4. **Unpack bytes**: Convert the 4 x 64-bit values back to the 32-byte flag string.

### Key insight for reversing the bitonic sort
The bitonic sort with direction `d` sorts elements. To reverse:
- Sort with direction `d^1` (opposite direction) reverses the permutation.
- The NOT and XOR operations between sorts are self-inverse (XOR twice = identity).

So to reverse `sub_406270`:
1. Reverse sort 3: sort with direction 0
2. XOR with `0x00000000FFFFFFFF`
3. Reverse sort 2: sort with direction 0
4. XOR with `0xFFFFFFFF00000000`
5. Reverse sort 1: sort with direction 0
6. NOT all bits
7. Reassemble from bit-decomposed form

## Implementation Plan

Write a Python script that:
1. Implements the bitonic sorting network on 256-bit values
2. Implements the bit decomposition and reassembly
3. Runs the inverse transformation
4. Extracts the flag

The script should be placed at `rev/(btw)/solve.py`.
