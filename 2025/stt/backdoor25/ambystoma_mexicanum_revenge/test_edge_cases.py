#!/usr/bin/env python3

# Test Python slicing behavior
data = b"0123456789ABCDEF"  # 16 bytes

# Normal slicing
print(f"data[0:16] = {data[0:16]}")
print(f"data[16:32] = {data[16:32]}")  # Out of bounds

# What if we manipulate i?
for i in [-1, 0, 1, 2, 3, 4]:
    start = 16 * i
    end = 16 * (i + 1)
    slice_result = data[start:end]
    print(f"i={i}: data[{start}:{end}] = {slice_result}")

# Testing unhexlify edge cases
import binascii

test_cases = [
    "",  # Empty
    "00",  # Single byte
    "0",  # Odd length (should fail)
    "zz",  # Invalid hex (should fail)
]

for tc in test_cases:
    try:
        result = binascii.unhexlify(tc)
        print(f"unhexlify('{tc}') = {result}")
    except Exception as e:
        print(f"unhexlify('{tc}') = ERROR: {e}")
