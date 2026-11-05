#!/usr/bin/env python3
"""
Solver for enigmaP CTF challenge (difficulty 0/1).

The binary performs:
1. Pack 32 flag bytes into 4 x 64-bit values (little-endian qwords)
2. Apply sub_406270 transformation (bit rotation + sorting network)
3. XOR result with SHA-256 initial values
4. Check no byte equals 0x40 ('@')
5. Apply sub_406270 again
6. Compare against target constants

sub_406270 does:
  a. Create 32 copies of the 256-bit input, each rotated left by 8*i bits
  b. NOT all entries
  c. Bitonic sort (direction=1, ascending)
  d. XOR all entries with 0xFFFFFFFF00000000 per qword
  e. Bitonic sort (direction=1, ascending)
  f. XOR all entries with 0x00000000FFFFFFFF per qword
  g. Bitonic sort (direction=1, ascending)
  h. Reassemble output from sorted entries
"""

import struct

MASK64 = 0xFFFFFFFFFFFFFFFF


def pack_bytes_to_qwords(flag_bytes):
    """Pack 32 bytes into 4 x 64-bit values (little-endian)."""
    assert len(flag_bytes) == 32
    q = []
    for i in range(4):
        val = 0
        for j in range(8):
            val |= flag_bytes[i * 8 + j] << (j * 8)
        q.append(val)
    return q


def unpack_qwords_to_bytes(qwords):
    """Unpack 4 x 64-bit values to 32 bytes."""
    result = []
    for q in qwords:
        for j in range(8):
            result.append((q >> (j * 8)) & 0xFF)
    return bytes(result)


def rotate_left_256(qwords, bits):
    """Rotate a 256-bit value (as 4 x 64-bit qwords, q0=LSB) left by `bits` bits."""
    # Treat as a single 256-bit number: val = q3<<192 | q2<<128 | q1<<64 | q0
    val = qwords[0] | (qwords[1] << 64) | (qwords[2] << 128) | (qwords[3] << 192)
    mask256 = (1 << 256) - 1
    bits = bits % 256
    val = ((val << bits) | (val >> (256 - bits))) & mask256
    return [
        val & MASK64,
        (val >> 64) & MASK64,
        (val >> 128) & MASK64,
        (val >> 192) & MASK64,
    ]


def compare_256(a, b):
    """
    Compare two 256-bit values (as [q0, q1, q2, q3]).
    Returns -1, 0, or 1.
    The binary compares q0 first, then q1, q2, q3 (lexicographic on qwords).
    """
    # From the assembly: it compares qword[0] first, then [1], [2], [3]
    for i in range(4):
        if a[i] != b[i]:
            return -1 if a[i] < b[i] else 1
    return 0


def bitonic_compare_and_swap(arr, i, j, direction):
    """Compare and conditionally swap elements i and j."""
    cmp = compare_256(arr[i], arr[j])
    if cmp != 0:
        should_swap = (cmp > 0) if direction == 1 else (cmp < 0)
        if should_swap:
            arr[i], arr[j] = arr[j], arr[i]


def bitonic_merge(arr, lo, n, direction):
    """Bitonic merge."""
    if n <= 1:
        return
    # Find greatest power of 2 less than n
    k = 1
    while k < n:
        k <<= 1
    k >>= 1

    for i in range(lo, lo + n - k):
        bitonic_compare_and_swap(arr, i, i + k, direction)

    bitonic_merge(arr, lo, k, direction)
    bitonic_merge(arr, lo + k, n - k, direction)


def bitonic_sort(arr, lo, n, direction):
    """Bitonic sort."""
    if n <= 1:
        return
    mid = n // 2
    # The binary uses: sort first half with direction^1, second half with direction
    bitonic_sort(arr, lo, mid, direction ^ 1)
    bitonic_sort(arr, lo + mid, n - mid, direction)
    bitonic_merge(arr, lo, n, direction)


def not_256(qwords):
    """Bitwise NOT of a 256-bit value."""
    return [q ^ MASK64 for q in qwords]


def xor_256(a, b):
    """XOR two 256-bit values."""
    return [a[i] ^ b[i] for i in range(4)]


def sub_406270_forward(input_qwords):
    """
    Forward transformation (sub_406270).
    Input: 4 x 64-bit qwords representing 256 bits.
    Output: 4 x 64-bit qwords.
    """
    # Step 1: Create 32 rotated copies
    arr = []
    for i in range(32):
        arr.append(rotate_left_256(input_qwords, i * 8))

    # Step 2: NOT all entries
    for i in range(32):
        arr[i] = not_256(arr[i])

    # Step 3: Bitonic sort (direction=1)
    bitonic_sort(arr, 0, 32, 1)

    # Step 4: XOR with 0xFFFFFFFF00000000 per qword
    xor_val_1 = [0xFFFFFFFF00000000, 0xFFFFFFFF00000000, 0xFFFFFFFF00000000, 0xFFFFFFFF00000000]
    for i in range(32):
        arr[i] = xor_256(arr[i], xor_val_1)

    # Step 5: Bitonic sort (direction=1)
    bitonic_sort(arr, 0, 32, 1)

    # Step 6: XOR with 0x00000000FFFFFFFF per qword
    xor_val_2 = [0x00000000FFFFFFFF, 0x00000000FFFFFFFF, 0x00000000FFFFFFFF, 0x00000000FFFFFFFF]
    for i in range(32):
        arr[i] = xor_256(arr[i], xor_val_2)

    # Step 7: Bitonic sort (direction=1)
    bitonic_sort(arr, 0, 32, 1)

    # Step 8: Reassemble output
    # The reassembly extracts the low byte of specific qwords from the sorted array
    # Each 256-bit entry is [q0, q1, q2, q3] at offsets 0x00, 0x08, 0x10, 0x18 within 0x20-byte entries
    # The code reads from offsets like i_3+0x18, i_3+0x118, i_3+0x218, i_3+0x318
    # Entry k starts at offset k*0x20
    # So offset 0x18 = entry 0, qword 3 (offset 0x18 within entry)
    # offset 0x118 = entry 8 (0x118/0x20 = 8.875 -> entry 8, offset 0x18) = entry 8, qword 3
    # Wait: 0x118 = 8*0x20 + 0x18 = entry 8, qword at offset 0x18 = q3
    # offset 0x218 = 16*0x20 + 0x18 = entry 16, q3
    # offset 0x318 = 24*0x20 + 0x18 = entry 24, q3

    # Let me map all the offsets used in the reassembly:
    # The pattern reads pairs of qwords and builds the output using shift-left-8 and OR with masked bytes

    # From the code, the reassembly reads:
    # First pair (most significant byte position):
    #   zmm0_3[lo] = [i_3+0x18, i_3+0x118]  = [entry 0 q3, entry 8 q3]
    #   zmm1_3     = [i_3+0x218, i_3+0x318]  = [entry 16 q3, entry 24 q3]
    #   zmm0_3 = [entry0.q3, entry8.q3, entry16.q3, entry24.q3]
    #
    # Second pair:
    #   zmm2[lo] = [i_3+0x38, i_3+0x138]  = [entry 1 q3, entry 9 q3]
    #   temp0_13 = [i_3+0x238, i_3+0x338]  = [entry 17 q3, entry 25 q3]
    #   zmm2 = [entry1.q3, entry9.q3, entry17.q3, entry25.q3]
    #
    # zmm0_3 = (zmm0_3 & 0xFF) << 8 | (zmm2 & 0xFF)
    #
    # Third pair (offset 0x58 = entry 2 q3, etc.):
    #   [entry2.q3, entry10.q3, entry18.q3, entry26.q3]
    # zmm0_3 = zmm0_3 << 8 | (third & 0xFF)
    #
    # And so on for entries 3, 4, 5, 6, 7 (using q3 of entries 3,11,19,27 etc.)

    # Wait, let me re-check. offset 0x58 within the array:
    # 0x58 / 0x20 = 2.75, so entry 2, offset 0x18 = q3. Yes.
    # offset 0x78 = entry 3, offset 0x18 = q3
    # offset 0x98 = entry 4, offset 0x18 = q3
    # offset 0xb8 = entry 5, offset 0x18 = q3
    # offset 0xd8 = entry 6, offset 0x18 = q3
    # offset 0xf8 = entry 7, offset 0x18 = q3

    # So the pattern is: for output qword k (k=0..3), we read entry[k*8+j].q3 for j=0..7
    # and build: result_qk = entry[k*8+0].q3_byte0 << 56 | entry[k*8+1].q3_byte0 << 48 | ... | entry[k*8+7].q3_byte0

    # Actually let me re-derive. The code builds zmm0_3 as a 256-bit value with 4 qwords.
    # zmm0_3 = [out_q0, out_q1, out_q2, out_q3]
    # 
    # For each "round" j=0..7:
    #   reads entry[j].q3, entry[8+j].q3, entry[16+j].q3, entry[24+j].q3
    #   masks each with 0xFF
    #   shifts zmm0_3 left by 8 and ORs
    #
    # So out_qk = sum over j=0..7 of (entry[k*8+j].q3 & 0xFF) << ((7-j)*8)
    # Wait, the first read is j=0 (entries 0,8,16,24), then j=1 (entries 1,9,17,25), etc.
    # The shift pattern is: first read gets shifted left 7 times (by 8 each), last read not shifted.
    # So: out_qk = (entry[k*8+0].q3 & 0xFF) << 56 | (entry[k*8+1].q3 & 0xFF) << 48 | ... | (entry[k*8+7].q3 & 0xFF)

    # But wait - the first zmm0_3 is masked with 0xFF and shifted left by 8, then OR'd with next masked value.
    # Then shifted left by 8 again, etc. After 7 shifts and 8 OR operations:
    # result = ((((((((b0 << 8) | b1) << 8) | b2) << 8) | b3) << 8) | b4) << 8 | b5) << 8 | b6) << 8 | b7
    # = b0 << 56 | b1 << 48 | b2 << 40 | b3 << 32 | b4 << 24 | b5 << 16 | b6 << 8 | b7

    # Hmm but looking at the code more carefully:
    # Line 5211: zmm0_3 = _mm256_slli_epi64(zmm0_3 & zmm1_3, 8) | zmm2;
    # This is: (zmm0_3 & 0xFF) << 8 | zmm2_masked
    # So first iteration: zmm0_3 has entry[0,8,16,24].q3
    #                     zmm2 has entry[1,9,17,25].q3 & 0xFF
    #   result = (entry[k*8].q3 & 0xFF) << 8 | (entry[k*8+1].q3 & 0xFF)
    #
    # Line 5215: zmm0_3 = _mm256_slli_epi64(zmm0_3, 8);
    # Line 5222: zmm0_3 = _mm256_slli_epi64(zmm0_3 | zmm2, 8);
    # Hmm, there's an extra shift. Let me re-trace...

    # Actually the pattern in the code is not perfectly regular. Let me just extract
    # the byte from q3 of each entry and build the output.

    # The output for each of the 4 qwords is built from 8 entries' q3 low bytes.
    # out_q0 uses entries 0,1,2,3,4,5,6,7
    # out_q1 uses entries 8,9,10,11,12,13,14,15
    # out_q2 uses entries 16,17,18,19,20,21,22,23
    # out_q3 uses entries 24,25,26,27,28,29,30,31

    result = [0, 0, 0, 0]
    for k in range(4):
        val = 0
        for j in range(8):
            byte_val = arr[k * 8 + j][3] & 0xFF  # q3, low byte
            val = (val << 8) | byte_val
        result[k] = val

    return result


def sub_406270_inverse(output_qwords):
    """
    Inverse of sub_406270.
    Given the output, recover the input.
    """
    # We need to reverse the process:
    # 1. From output qwords, reconstruct the sorted array (step 8 inverse)
    # 2. Reverse sort 3
    # 3. Reverse XOR with 0x00000000FFFFFFFF
    # 4. Reverse sort 2
    # 5. Reverse XOR with 0xFFFFFFFF00000000
    # 6. Reverse sort 1
    # 7. Reverse NOT
    # 8. From the 32 rotated copies, extract the original value

    # The problem: step 8 inverse is hard because we only know the low byte of q3
    # for each sorted entry. We don't know the full 256-bit values.

    # Alternative approach: brute force is infeasible for 256 bits.
    # But we can use the forward function and try to find the input.

    # Better approach: since the transformation is deterministic and the flag
    # is printable ASCII, we can try a different strategy.

    # Actually, the key insight is that sub_406270 is applied TWICE in the
    # verification. Let me re-read the verification flow:
    #
    # 1. Pack flag -> qwords
    # 2. result1 = sub_406270(qwords)
    # 3. xored = result1 XOR sha256_iv
    # 4. Check no byte == 0x40
    # 5. result2 = sub_406270(xored)
    # 6. Compare result2 against target
    #
    # So we need: sub_406270_inverse(target) = xored
    #             xored XOR sha256_iv = result1
    #             sub_406270_inverse(result1) = qwords
    #             unpack qwords = flag

    # The issue is inverting sub_406270. Let me think about this differently.
    #
    # sub_406270 creates 32 rotations of the input, applies NOT, sorts them,
    # applies some XOR+sort steps, then extracts bytes.
    #
    # The sorting network is a COMPARISON-BASED sort. It sorts 32 elements
    # of 256 bits each. The sort is deterministic given the comparison function.
    #
    # To invert: we need to find what 256-bit value, when rotated 32 ways,
    # NOT'd, and sorted (with the XOR steps), produces the target output.
    #
    # This is essentially: given the sorted output, find the permutation
    # that was applied, then invert it to get the original rotated values,
    # then un-NOT and un-rotate to get the input.
    #
    # But we don't have the full sorted array - only the low byte of q3
    # of each entry. However, the sorted entries ARE the NOT'd rotations
    # of the input (after the XOR steps). So if we know the input, we can
    # verify. But we need to find the input.
    #
    # Let me think about what the sorted array looks like.
    # After step 2 (NOT), we have 32 values that are NOT(rotate(input, i*8)).
    # After sorting, these are in ascending order.
    # After XOR with 0xFFFFFFFF00000000, the upper 32 bits of each qword are flipped.
    # After sorting again, and XOR with 0x00000000FFFFFFFF, lower 32 bits flipped.
    # After final sort.
    #
    # This is getting complex. Let me try a completely different approach:
    # just implement the forward function and brute-force character by character
    # using the structure of the flag.

    # Actually, the simplest approach: since the flag is CSCPT{...} format,
    # we know 7 characters. The remaining 25 characters are unknown.
    # 25 characters is too many to brute force.

    # Let me reconsider the mathematical structure.
    # The 32 rotations of a 256-bit value by multiples of 8 bits are just
    # the 32 byte-rotations. After NOT, we sort these 32 byte-rotations.
    #
    # Key insight: sorting the 32 byte-rotations of a value is equivalent
    # to finding the sorted order of all cyclic byte-rotations.
    # This is related to the Burrows-Wheeler Transform!
    #
    # After the NOT+sort+XOR+sort+XOR+sort sequence, the result is a
    # specific permutation of the byte-rotations.
    #
    # But we only extract one byte from each sorted entry (the low byte of q3,
    # which is byte 24 of the 256-bit value). This IS the last column of the
    # BWT matrix!
    #
    # So sub_406270 computes something like a BWT of the 32-byte input,
    # but with additional XOR steps between sorts.

    # Let me try yet another approach: implement the forward function correctly
    # and verify with a known input, then use Z3 or similar to solve.
    pass


def verify_forward(flag_bytes):
    """Run the full forward verification (difficulty 1 path)."""
    assert len(flag_bytes) == 32

    # Step 1: Pack bytes to qwords
    qwords = pack_bytes_to_qwords(flag_bytes)

    # Step 2: First sub_406270
    result1 = sub_406270_forward(qwords)

    # Step 3: XOR with SHA-256 initial values
    sha256_iv = [
        0x67452301EFCDAB89,
        0x98BADCFE10325476,
        0x6A09E667BB67AE85,
        0x3C6EF372A54FF53A,
    ]
    xored = xor_256(result1, sha256_iv)

    # Step 4: Check for '@' (0x40) bytes
    xored_bytes = unpack_qwords_to_bytes(xored)
    has_at = any(b == 0x40 for b in xored_bytes)
    if has_at:
        xored = [0, 0, 0, 0]

    # Step 5: Second sub_406270
    result2 = sub_406270_forward(xored)

    # Step 6: Compare against target
    target = [
        0x6DB9DA380B5584C7,
        0x8A1840A1DA251624,
        0x5E1CB4AC237ADE56,
        0x141E12C1ECFD8EFB,
    ]

    return result2 == target


def solve_with_z3():
    """Use Z3 SMT solver to find the flag."""
    try:
        from z3 import BitVec, BitVecVal, Solver, sat, Extract, Concat, If, And
    except ImportError:
        print("Z3 not available, trying alternative approach")
        return None

    print("Setting up Z3 solver...")

    # Create 32 byte variables for the flag
    flag_vars = [BitVec(f'f{i}', 8) for i in range(32)]

    solver = Solver()

    # Known prefix: CSCPT{
    known = b'CSCPT{'
    for i, c in enumerate(known):
        solver.add(flag_vars[i] == c)

    # Known suffix: }
    solver.add(flag_vars[31] == ord('}'))

    # All characters are printable ASCII
    for i in range(6, 31):
        solver.add(flag_vars[i] >= 0x20)
        solver.add(flag_vars[i] <= 0x7E)

    # Pack into 4 x 64-bit values
    qwords_z3 = []
    for i in range(4):
        q = BitVecVal(0, 64)
        for j in range(8):
            byte_ext = Concat(BitVecVal(0, 56), flag_vars[i * 8 + j])
            q = q | (byte_ext << (j * 8))
        qwords_z3.append(q)

    # This approach won't work well because the sorting network
    # involves comparisons which create exponential branching in Z3.
    # Let me try a different approach.
    print("Z3 approach with sorting network is too complex.")
    print("Trying direct computation approach instead.")
    return None


def solve_direct():
    """
    Direct solving approach.

    Since sub_406270 creates 32 byte-rotations, NOTs them, and sorts,
    the output bytes (extracted from q3 byte 0 of each sorted entry)
    form a specific transform of the input.

    Let's think about what happens with the three sort+XOR rounds:

    Round 1: NOT all, sort ascending
    Round 2: XOR upper32 of each qword, sort ascending
    Round 3: XOR lower32 of each qword, sort ascending

    The NOT in round 1 reverses the sort order (sorting NOT(x) ascending
    = sorting x descending). The XOR steps in rounds 2 and 3 modify
    the comparison keys.

    Actually, let me reconsider. The XOR between sorts changes the values
    being sorted, not just the comparison. So after NOT+sort, we have
    sorted NOT(rotations). Then XOR with pattern changes the values,
    then sort again, etc.

    Let me just try to compute the forward function on test inputs
    and see if I can understand the pattern.
    """

    # Let's verify with a simple test first
    test_input = b'CSCPT{AAAAAAAAAAAAAAAAAAAAAAAAA}'
    print(f"Testing with: {test_input}")
    qwords = pack_bytes_to_qwords(test_input)
    print(f"Packed qwords: {[hex(q) for q in qwords]}")

    result = sub_406270_forward(qwords)
    print(f"sub_406270 result: {[hex(q) for q in result]}")

    # XOR with SHA-256 IV
    sha256_iv = [
        0x67452301EFCDAB89,
        0x98BADCFE10325476,
        0x6A09E667BB67AE85,
        0x3C6EF372A54FF53A,
    ]
    xored = xor_256(result, sha256_iv)
    print(f"After XOR with IV: {[hex(q) for q in xored]}")

    xored_bytes = unpack_qwords_to_bytes(xored)
    print(f"XORed bytes: {xored_bytes.hex()}")
    has_at = any(b == 0x40 for b in xored_bytes)
    print(f"Has '@' byte: {has_at}")

    if not has_at:
        result2 = sub_406270_forward(xored)
        print(f"Second sub_406270: {[hex(q) for q in result2]}")

    target = [
        0x6DB9DA380B5584C7,
        0x8A1840A1DA251624,
        0x5E1CB4AC237ADE56,
        0x141E12C1ECFD8EFB,
    ]
    print(f"\nTarget: {[hex(t) for t in target]}")


def solve_by_inverting():