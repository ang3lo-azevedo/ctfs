#!/usr/bin/env python3
"""
Solve 'Linear' CTF challenge.

Each 4-byte chunk of the 56-byte flag goes through a linear-over-GF(2)
transformation F_i(x). Since F_i is linear:
    F_i(x) = A_i * x ^ b_i
where A_i is a 32x32 GF(2) matrix and b_i = F_i(0).

We recover A_i and b_i by probing 33 inputs via GDB, then solve:
    A_i * x = expected_i ^ b_i  =>  x = A_i^{-1} * (expected_i ^ b_i)
"""

import subprocess
import struct
import sys

GDB   = "/nix/store/7npv5s0lj8l1yhwn89qzqqwzcfjj5gxn-gdb-17.1/bin/gdb"
BIN   = "/home/ang3lo/Documents/ctfs/solo/26/cscpt/quals/rev/Linear/linear.elf"
BUF   = 0x41e030   # input_buf address (no PIE)
BPAFTER_SCANF = 0x401157  # right after scanf returns

# (comparison address, expected eax)
CHUNKS = [
    (0x402fc0, 0x70cdf1b0),
    (0x404e8c, 0x46b67718),
    (0x406c6d, 0x8212ce01),
    (0x4089fb, 0xb6a61439),
    (0x40a7f0, 0x42ddc1fa),
    (0x40c5b3, 0x284c1f25),
    (0x40e3c7, 0x6b35615e),
    (0x410161, 0xb9cc2e00),
    (0x412050, 0xf18ab873),
    (0x413fe4, 0x0dac14c3),
    (0x415e56, 0x0af18e91),
    (0x417be8, 0x36ad92a9),
    (0x419add, 0x70cc2cbf),
    (0x41b97b, 0x2501c822),
]


def probe(chunk_idx: int, chunk_val: int) -> int:
    """Return eax at CHUNKS[chunk_idx] comparison when chunk bytes = chunk_val."""
    cmp_addr, _ = CHUNKS[chunk_idx]

    # 57-byte buffer: all 0x41 ('A') except chunk bytes
    buf = bytearray(b'A' * 57)
    struct.pack_into("<I", buf, chunk_idx * 4, chunk_val)
    buf[56] = 0  # null terminator

    mem_set = ",".join(str(b) for b in buf)

    result = subprocess.run(
        [GDB, "-batch",
         "-ex", f"file {BIN}",
         "-ex", f"break *{BPAFTER_SCANF:#x}",
         "-ex", "run",          # stdin comes from our pipe
         "-ex", f"set {{char[57]}} {BUF:#x} = {{{mem_set}}}",
         "-ex", f"break *{cmp_addr:#x}",
         "-ex", "continue",
         "-ex", "print/x $eax",
         "-ex", "quit"],
        input=b"A" * 56 + b"\n",
        capture_output=True, timeout=30
    )
    for line in result.stdout.decode(errors="replace").splitlines():
        if "$" in line and "0x" in line:
            return int(line.split("0x")[1].split()[0].rstrip(")"), 16)
    raise RuntimeError(
        f"GDB parse fail (chunk={chunk_idx}, val={chunk_val:#010x}):\n"
        f"{result.stdout.decode(errors='replace')}\n{result.stderr.decode(errors='replace')}"
    )


# ── GF(2) linear algebra ──────────────────────────────────────────────────────

def mat_vec(A: list, v: int) -> int:
    """Multiply 32×32 GF(2) matrix A (list of 32 column ints) by bit-vector v."""
    r = 0
    for j, col in enumerate(A):
        if (v >> j) & 1:
            r ^= col
    return r


def mat_inv(A: list) -> list:
    """Invert 32×32 GF(2) matrix using Gaussian elimination (column basis)."""
    M = list(A)
    I = [1 << j for j in range(32)]
    for col in range(32):
        pivot = next((r for r in range(col, 32) if (M[r] >> col) & 1), None)
        if pivot is None:
            raise ValueError(f"Singular matrix at column {col}")
        M[col], M[pivot] = M[pivot], M[col]
        I[col], I[pivot] = I[pivot], I[col]
        for row in range(32):
            if row != col and (M[row] >> col) & 1:
                M[row] ^= M[col]
                I[row] ^= I[col]
    return I


# ── Main ──────────────────────────────────────────────────────────────────────

def solve_chunk(i: int) -> bytes:
    _, expected = CHUNKS[i]
    print(f"[chunk {i:2d}] probing (33 GDB calls)...", flush=True)

    b = probe(i, 0)                     # constant term F(0)
    A = []
    for j in range(32):
        fj = probe(i, 1 << j)          # F(1<<j)
        A.append(fj ^ b)               # j-th column of matrix A

    A_inv = mat_inv(A)
    x = mat_vec(A_inv, expected ^ b)
    xb = struct.pack("<I", x & 0xFFFFFFFF)
    printable = xb.decode("latin-1")
    print(f"         expected={expected:#010x}  F(0)={b:#010x}  x={x:#010x}  bytes={xb!r}  {printable!r}")
    return xb


def main():
    flag = bytearray()
    for i in range(len(CHUNKS)):
        flag += solve_chunk(i)

    print(f"\n==> Flag: {flag.decode('latin-1', errors='replace')}")

    # Verify
    result = subprocess.run(BIN, input=flag + b"\n", capture_output=True, timeout=10)
    print(f"==> Binary output: {result.stdout.decode().strip()}")


if __name__ == "__main__":
    main()
