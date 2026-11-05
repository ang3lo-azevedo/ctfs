# NOT OCB3 - CSCPT CTF 2026 Quals Writeup

**Category:** Crypto  
**Challenge:** NOT OCB3  
**Flag:** `CSCPT{}` *(pending solve)*

## Challenge Description

A custom implementation of OCB3 authenticated encryption with a deliberate mistake. The server lets us encrypt/decrypt with chosen plaintext (built from 200 known hex chunks) and we need to forge a valid ciphertext.

Server: `nc challenges.cybersecuritychallenge.pt 26303`

## Code Analysis

### The Mistake

The bug is in the `_tag_block` function in `utils.py` at **line 90**:

```python
def _tag_block(self, checksum, offset_0, has_tail):
    tag_offset = offset_0
    if has_tail:
        tag_offset = xor_bytes(tag_offset, self.L_star)
    tag_input = xor_bytes(checksum, tag_offset)
    tag_input = xor_bytes(tag_input, self.L_dollar)  # <-- BUG: extra XOR
    return self._aes_encrypt(tag_input)
```

**Standard OCB3** (RFC 7253) tag computation:
```
tag = E_K(checksum ⊕ offset_0 ⊕ [L_star if tail]) ⊕ hash_aad(aad)
```

**This implementation:**
```
tag = E_K(checksum ⊕ offset_0 ⊕ [L_star if tail] ⊕ L_dollar) ⊕ hash_aad(aad)
```

The extra XOR with `L_dollar = 2 × L_star` is a deviation from the spec. `L_dollar` should only be used in the L-chain (`L[0] = 4L`, etc.), not in the tag tweak.

### Relationship to OCB2 Vulnerability

This is the same class of bug that broke OCB2 (Poettering 2018, Inoue-Minematsu 2018). In OCB2, the tag tweak `L_star ⊕ L_dollar = 3L` collided with the tweak for block 3, enabling ciphertext block swapping. Here, the tag tweaks are:
- No tail: `L_dollar = 2L`
- With tail: `L_star ⊕ L_dollar = 3L`

While OCB3's block tweaks (starting at `4L, 12L, 8L, 24L, ...`) don't directly collide with `2L` or `3L`, the deviation still weakens security.

### Key Cryptographic Relation

When `checksum ⊕ L_dollar = P_1 ⊕ L[0]` (i.e., `checksum = P_1 ⊕ 6L*`), the tag input equals block 1's encryption input:

```
tag_input = checksum ⊕ offset_0 ⊕ L_dollar
          = P_1 ⊕ 6L* ⊕ offset_0 ⊕ 2L*
          = P_1 ⊕ 4L* ⊕ offset_0
          = P_1 ⊕ L[0] ⊕ offset_0
          = P_1 ⊕ Δ_1
          = block_1_input
```

Then:
```
T = E_K(P_1 ⊕ Δ_1) = C_1 ⊕ Δ_1
=> Δ_1 = C_1 ⊕ T                       (we recover block 1's offset!)
=> L* = (P_1 ⊕ checksum) × 6^(-1)     (we recover the key-dependent L*!)
```

Once `L*` is known, all L-values are computable and universal forgery is trivial.

## Attack Strategy (from epring 2023/326)

The paper [A Weakness in OCB3 used with short nonces](https://eprint.iacr.org/2023/326) shows:

1. With **empty nonce** (`len=0`), `nonce_block = [0×16]` after masking → `ktop = E_K(0) = L*`  
   Probability of success: 1/4

2. With **short nonces** (`1-5 bytes`), there are only **4 possible nonce_block values** (2 effective bits), each with 64 possible `offset_0` values  
   Total: 256 possible `offset_0` values for 1-byte nonces

3. The tag-ciphertext relationship from the `L_dollar` bug enables recovery of `Δ_1` when the checksum condition holds, revealing `L*`

### Solution Outline

1. Collect many encrypted plaintexts (different chunk combinations)
2. For each, check if `checksum = P_1 ⊕ 6L*` condition holds (probability 2^(-128)/attempt)  
   Or: use short nonces (1-byte) in decrypt oracle to enumerate possibilities
3. Recovery: `Δ_1 = C_1 ⊕ T` → `L* = (P_1 ⊕ cs) / 6` in GF(2^128)
4. Compute all L values and forge arbitrary ciphertext/tag pairs
5. Forge a valid decryption for a previously unseen chunk combination → flag

## Files

- `not_ocb3.py` - Server challenge code
- `utils.py` - Custom OCB3 implementation (contains the bug)
- `2023-326.pdf` - Reference paper describing the short-nonce weakness

## Status

The bug has been identified and the attack path is clear. Full exploitation requires implementing the paper's L*-recovery technique for the short-nonce case (Section 4.3), which needs further work on mapping the probabilistic offset relationship when `nonce_block ≠ 0`.
