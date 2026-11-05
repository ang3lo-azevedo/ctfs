---
title: Obj2ctm Writeup
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['pwn', 'heap', 'OOB']
summary: 'Exploiting unvalidated face indices in OBJ parser to achieve OOB read/write'
canonical: ''
---

## Obj2ctm

### Vulnerability Analysis

The challenge consists of:
- `obj2ctm`: Main PIE binary, a fork server that accepts OBJ files and converts them to CTM
- `libfastobj.so`: Fast OBJ parsing library
- `libopenctm.so`: CTM file format library

**Protocol**: Little-endian 4-byte size prefix followed by OBJ data. The server forks for each connection.

**Key Bugs**:

1. **Uninitialized `mesh->object_count`** (at offset 0x60): The `fastObjMesh` struct has its `object_count` field uninitialized when no `o` lines are present. The `convert()` function uses this field as the loop bound for the UV swizzle pass, leading to either 0 iterations (no write) or massive over-iteration (processing garbage as indices).

2. **No bounds checking on face indices**: The OBJ parser (`libfastobj.so`) stores face vertex position/texcoord/normal indices without validating them against the actual array sizes. This allows arbitrary OOB read/write via the UV swizzle loop.

3. **Swizzle bug in `convert()`**: The UV swizzle loop incorrectly uses `mesh->texcoords[t]` as the source and writes to `texcoord_dst[p]` (where `p` and `t` are the face vertex indices). Since both indices are attacker-controlled, this provides:
   - **OOB Read**: `texcoords[2*t]` at large `t` reads past the texcoords heap allocation
   - **OOB Write**: `texcoord_dst[2*p]` at large `p` writes past the `texcoord_dst` calloc buffer into the adjacent CTM context

### Exploit Strategy

#### Stage 1: Heap Leak

Send OBJ with:
- 3 vertices, 1 texcoord, face `f 8/8 2/1 3/1`
- The UV swizzle processes indices[0]={p:8, t:8}, writing `texcoords[16]` (heap data) to `ctx+0x10` (vertexCount)
- This triggers a massive OOB read that dumps heap contents into the CTM UV map

#### Stage 2: Arbitrary Write

With known relative offsets from `texcoord_dst`:
- `ctx+0x68` (comment pointer): p = 19 → controls what string gets written by `_ctmStreamWriteSTRING`
- `ctx+0x78` (write callback): p = 21 → controls the function called for CTM output

The write callback is invoked as `ctx->write_fn(data, size, ctx->user_data)`.

By overwriting `ctx->write_fn` with `system` and `ctx->comment` with a pointer to a controlled command string, then overwriting `ctx->comment` to point to that string, the CTM library calls `system(cmd)` when writing the comment.

#### Key Obstacle: Float Encoding

The OOB write sources values from the texcoords array, which is populated via OBJ `vt` (texture coordinate) lines. These accept only decimal float strings. IEEE 754 subnormal floats (< 0x00800000) lose precision when round-tripped through decimal strings, making it impossible to encode the high 32 bits of 64-bit pointers (e.g., 0x00007Fxx or 0x000055xx).

**Workaround**: The high 32 bits of the existing `ctx->write_fn` (PIE address) are already correct. By only partially overwriting the low 32 bits (requires single-float write granularity), or by using a libc one_gadget with both halves in normal float range, the write becomes feasible.

#### libc Offsets (Ubuntu GLIBC 2.39)
- `system`: 0x58750
- `/bin/sh`: 0x1cb42f  
- one_gadget: 0xef4ce (constraints: execve("/bin/sh", rbp-0x50, r12))

### Exploit Script

```python
# Key functions:
# - send_obj(): Send OBJ data to server
# - parse_ctm_texc(): Extract UV map data from CTM response
# - u64_to_floats(): Convert 64-bit pointer to two float values for vt lines
# 
# Full exploit requires:
# 1. CTM decompression to parse leaked heap/libc addresses
# 2. Encoding target pointer in vt entries (handle subnormal issue)
# 3. Face construction with correct p/t values for OOB write to ctx fields
```

### Flag

`CSCPT{...}` (requires completing the CTM parsing and address leak chain)
