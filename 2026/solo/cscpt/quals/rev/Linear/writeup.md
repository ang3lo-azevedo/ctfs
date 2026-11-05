---
title: Linear
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['rev', 'crc32', 'linear-algebra', 'gf2', 'cmov']
summary: 'Branchless x86-64 binary that checks a 56-byte flag using two CRC32 passes per 4-byte chunk. The cmov obfuscation is noise; the real check is a linear map over GF(2) inverted with 33 GDB probes per chunk.'
canonical: ''
---

## Linear

## Table of Contents

1. [Source](#source)
2. [Solution](#solution)

## Source

A single 123 KB x86-64 ELF. No PIE, dynamically linked. The challenge description says "no branches" and "prints `good!` when the flag is correct."

## Solution

### Step 1 — Understanding the structure

Running `objdump -d` reveals that `main` contains over **22 000 `cmov` instructions** and zero conditional jumps. The `cmov` noise falls into two categories:

1. **Self-moves after `cmp %r13d,%r13d`** — comparing a register with itself always sets ZF=1, CF=0, so every subsequent `cmovb`, `cmovne`, `cmova` is a no-op, and every `cmovae`, `cmove`, `cmovge`, `cmovle` moves a register into itself. Pure padding.

2. **The one real `cmov` per CRC bit** — after a meaningful `cmp $0x0,%edx` the instruction `cmovne %ecx,%r11d` (or `cmove %ecx,%eax`) conditionally applies the CRC polynomial. This is the actual algorithm.

Ignoring the noise, the function:

- Reads 56 bytes from stdin with `scanf("%127s", input_buf)`.
- Checks `input_buf[56] == 0` (null terminator → exactly 56 chars).
- Processes the input as **14 independent 4-byte chunks** (offsets 0, 4, 8, … 52).

For each chunk `i` it:

1. Loads the 4 bytes as a little-endian 32-bit integer into `eax`.
2. XORs `eax` with several constants (obfuscated across many instructions).
3. Runs a **bit-by-bit CRC32** (poly `0xEDB88320`, init `0xFFFFFFFF`) on the resulting 4 bytes — pass 1.
4. XORs the CRC output with more constants.
5. Runs a second **bit-by-bit CRC32** pass.
6. Applies a final XOR (present on some chunks, absent on others).
7. Compares `eax` with a hardcoded expected value; updates a running "all-good" flag in `r12d`.

At the end, `r12d == 1` iff every chunk matched, and the binary prints `good!` or `bad`.

### Step 2 — Recognising linearity

XOR is linear over GF(2). CRC32 (bit-by-bit LFSR) is also a linear map over GF(2): each output bit is an XOR of a subset of input bits. Therefore the full per-chunk transformation

```
F_i(x) = postXOR( CRC2( interXOR( CRC1( preXOR(x) ) ) ) )
```

is a **linear map over GF(2)³²**:

```
F_i(x) = A_i · x  ⊕  b_i
```

where `A_i` is a 32×32 binary matrix and `b_i = F_i(0)`.

Importantly, we do **not** need to manually extract the dozens of XOR constants scattered through 14 × ~1500 instructions — we can recover `A_i` and `b_i` by black-box probing.

### Step 3 — Black-box matrix recovery

For each chunk `i` we make **33 GDB calls**:

| probe | input chunk | result |
|-------|-------------|--------|
| 0 | `0x00000000` | `b_i = F_i(0)` |
| j ∈ 0..31 | `1 << j` | `F_i(1<<j)` |

Column `j` of `A_i` is `F_i(1<<j) ⊕ b_i`.

In each GDB call we:
1. Break right after `scanf` returns.
2. Overwrite `input_buf` with our test value (chunk `i` bytes set to the probe, all others `'A'`).
3. Continue to the comparison instruction for chunk `i`.
4. Read `eax`.

### Step 4 — Solving the system

Given `A_i` and `b_i`, we want `x` such that

```
A_i · x ⊕ b_i = expected_i
  =>  A_i · x = expected_i ⊕ b_i
  =>  x = A_i⁻¹ · (expected_i ⊕ b_i)
```

`A_i` is invertible (CRC32 is a bijection on 4-byte inputs); standard Gaussian elimination over GF(2) gives `A_i⁻¹`.

Expected values per chunk (from the `cmp $CONST,%eax` instructions):

| chunk | bytes | expected |
|-------|-------|----------|
| 0 | 0–3 | `0x70cdf1b0` |
| 1 | 4–7 | `0x46b67718` |
| 2 | 8–11 | `0x8212ce01` |
| 3 | 12–15 | `0xb6a61439` |
| 4 | 16–19 | `0x42ddc1fa` |
| 5 | 20–23 | `0x284c1f25` |
| 6 | 24–27 | `0x6b35615e` |
| 7 | 28–31 | `0xb9cc2e00` |
| 8 | 32–35 | `0xf18ab873` |
| 9 | 36–39 | `0x0dac14c3` |
| 10 | 40–43 | `0x0af18e91` |
| 11 | 44–47 | `0x36ad92a9` |
| 12 | 48–51 | `0x70cc2cbf` |
| 13 | 52–55 | `0x2501c822` |

### Step 5 — Solver script

```python
# solve.py (abridged)
def probe(chunk_idx, chunk_val):
    """Return eax at comparison point via GDB."""
    ...

def solve_chunk(i):
    _, expected = CHUNKS[i]
    b = probe(i, 0)
    A = [probe(i, 1 << j) ^ b for j in range(32)]
    A_inv = gf2_mat_inv(A)
    x = gf2_mat_mul(A_inv, expected ^ b)
    return struct.pack("<I", x)

flag = b"".join(solve_chunk(i) for i in range(14))
# => b'CSCPT{cm0v_1s_4lw4ys_4s_c00l_4s_m4tr1x_mult1pl1c4t10n!.}'
```

Running the solver (462 GDB calls total, ~3 minutes) and verifying:

```
$ python3 solve.py
...
==> Flag: CSCPT{cm0v_1s_4lw4ys_4s_c00l_4s_m4tr1x_mult1pl1c4t10n!.}
==> Binary output: good!
```

### Flag

```
CSCPT{cm0v_1s_4lw4ys_4s_c00l_4s_m4tr1x_mult1pl1c4t10n!.}
```

The title gives it away: `cmov` is always as cool as matrix multiplication — because it *is* matrix multiplication (over GF(2)).
