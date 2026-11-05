---
title: Injected
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['pwn', 'stack-overflow', 'inet_aton']
summary: 'Stack buffer overflow via inet_aton write to local buffer, overwriting return address to call system("/bin/sh")'
canonical: ''
---

## Injected

**Category**: Pwn
**Points**: 500
**Flag**: `CSCPT{h0p3_y0u_d1dnt_1nject_m3}`

## Table of Contents

1. [Reconnaissance](#Reconnaissance)
2. [Vulnerability](#Vulnerability)
3. [Exploitation](#Exploitation)

## Reconnaissance

The binary is a 64-bit ELF with the following protections:

- **No PIE** (base at 0x400000)
- **No canary**
- **NX enabled** (no shellcode execution)

Key functions identified via disassembly:

- `main` (0x40142b): Reads up to 0x200 bytes from stdin, tokenizes on commas, stores up to 63 tokens in `g_tok[]`
- `store_and_ping` (0x40135a): Iterates tokens, calls `inet_aton(g_tok[g_i], &buf[g_i])` then `doit(g_tok[g_i])`
- `doit` (0x4012b6): Forks, runs `ping -c 1 -W 1 <IP>` via `execlp`
- A dead code path at 0x40132a calls `system("/bin/sh")` (never reached normally)

Strings of interest at:
- `0x402015`: `"/bin/sh"`
- `0x402010`: `"ping"`

## Vulnerability

In `store_and_ping`, a **16-byte local buffer** (at `rbp-0x10`) is indexed by `g_i` without bounds checking:

```
for (g_i = 0; g_i < g_n; g_i++) {
    inet_aton(g_tok[g_i], &buf[g_i]);  // writes 4 bytes at buf + g_i*4
    printf("pinging %s\n", g_tok[g_i]);
    doit(g_tok[g_i]);
}
```

Since `g_n` can be up to 63, `inet_aton` writes past the buffer starting at g_i=4:

| g_i | Offset    | Overwrites                  |
|-----|-----------|-----------------------------|
| 0-3 | rbp-0x10  | Local buffer (16 bytes)     |
| 4   | rbp+0x00  | Saved RBP (low 4 bytes)     |
| 5   | rbp+0x04  | Saved RBP (high 4 bytes)    |
| 6   | rbp+0x08  | Return address (low 4 bytes)|
| 7   | rbp+0x0c  | Return address (high 4 bytes)|

`inet_aton` stores the result in **network byte order**. To write a target address, each octet becomes an IP component in big-endian order. For little-endian addresses like `0x40132a`, the IP string is `42.19.64.0` (since bytes are stored as `[0x2a, 0x13, 0x40, 0x00]`).

## Exploitation

The target is the dead-code gadget at `0x40132a` inside `doit`:

```asm
0x40132a: lea rax, [rip+0xce4]   ; rax = "/bin/sh"
0x401331: mov rdi, rax            ; rdi = "/bin/sh"
0x401334: call system@plt         ; system("/bin/sh")
```

The exploit sends 8 comma-separated IP addresses:

```
8.8.8.8,8.8.8.8,8.8.8.8,8.8.8.8,8.8.8.8,8.8.8.8,42.19.64.0,0.0.0.0
```

- IPs 0-5: Arbitrary valid IPs (padding)
- IP 6 (`42.19.64.0`): Low 4 bytes of return address → `0x0040132a`
- IP 7 (`0.0.0.0`): High 4 bytes of return address → `0x00000000`

When `store_and_ping` returns, execution jumps to the `system("/bin/sh")` gadget, spawning a shell.
