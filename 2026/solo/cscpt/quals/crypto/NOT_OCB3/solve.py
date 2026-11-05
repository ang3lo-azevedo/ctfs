#!/usr/bin/env python3
"""
NOT OCB3 - Direct exploitation using multiple encryptions.

Key insight: the first plaintext block P1 = "your beautiful p" is
ALWAYS the same across ALL encryptions. 

For two encryptions of the SAME message with nonces Na and Nb:
  C_a[1] = E(P1 ^ Da_1) ^ Da_1    where Da_1 = offset_a ^ L[0]
  C_b[1] = E(P1 ^ Db_1) ^ Db_1    where Db_1 = offset_b ^ L[0]
  
  Da_1 ^ Db_1 = offset_a ^ offset_b = D (constant!)

  T_a = E(cs ^ offset_a ^ flag ^ L_dollar)
  T_b = E(cs ^ offset_b ^ flag ^ L_dollar)

From the L_dollar bug:
  T = E(cs ^ offset ^ flag ^ L_dollar)  [no tail]

If cs ^ L_dollar = P1 ^ L[0] (the magic condition, prob 2^-128):
  C_1 = E(P1 ^ offset ^ L[0]) ^ (offset ^ L[0])
  T   = E(P1 ^ offset ^ L[0])           [same E_K input!]
  So: T = C_1 ^ Delta_1, meaning Delta_1 = C_1 ^ T

For TWO encryptions of same message:
  Delta_a = C_a[1] ^ T_a
  Delta_b = C_b[1] ^ T_b
  D = Delta_a ^ Delta_b

And L* = (P1 ^ cs ^ flag) / 6 in GF(2^128)

BUT the condition has prob 2^(-128). However, we can CHECK
if the condition holds by verifying D across ALL blocks!

For ANY two encryptions of the SAME message:
  C_a[i] ^ C_b[i] = E(P_i ^ Delta_a[i]) ^ E(P_i ^ Delta_b[i]) ^ D

  Delta_a[i] ^ Delta_b[i] = D (same for all i!)

So: for ALL i, Delta_a[i] ^ Delta_b[i] should equal D.
But we can't compute Delta without the condition.

STRATEGY: Don't wait for the condition. Instead, use MULTIPLE
encryptions to build a SYSTEM OF EQUATIONS and solve for L*.

For block i of encrypt a: E_K(P_i ^ Delta_a[i]) = C_a[i] ^ Delta_a[i]
For block i of encrypt b: E_K(P_i ^ Delta_b[i]) = C_b[i] ^ Delta_b[i]

Delta_b[i] = Delta_a[i] ^ D

So: E_K(P_i ^ Delta_a[i] ^ D) = C_b[i] ^ Delta_a[i] ^ D

E_K(X) = C_a[i] ^ Delta_a[i]   where X = P_i ^ Delta_a[i]
E_K(X ^ D) = C_b[i] ^ Delta_a[i] ^ D

For the tag:
E_K(cs ^ offset_a ^ L_d) = T_a
E_K(cs ^ offset_b ^ L_d) = T_b

offset_b = offset_a ^ D

E_K(Y) = T_a   where Y = cs ^ offset_a ^ L_d
E_K(Y ^ D) = T_b

This is: E_K at inputs X, X^D, Y, Y^D. Four E_K calls.
Unknowns: X, Y, D (3 unknowns). Each E_K call is a 128-bit output.
We have 4 equations but E_K is a PRP (nonlinear). Can't solve.

HOWEVER: if we use a THIRD encryption of the same message:
E_K(X ^ D') = C_c[i] ^ Delta_a[i] ^ D'  where D' = Delta_a ^ Delta_c
E_K(Y ^ D') = T_c

Now: E_K(X), E_K(X^D), E_K(X^D'), E_K(Y), E_K(Y^D), E_K(Y^D')
6 equations, 4 unknowns (X, Y, D, D'). Still can't solve.

BUT: what if we consider a SECOND plaintext block i=2?
E_K(P_2 ^ Delta_a[2]) = C_a[2] ^ Delta_a[2]
Delta_a[2] = Delta_a[1] ^ L[1]

So: Delta_a[2] = (offset_a ^ L[0]) ^ L[1] = offset_a ^ 12L  [for 2 blocks]

And: E_K(P_2 ^ offset_a ^ 12L) = C_a[2] ^ offset_a ^ 12L

Now we have E_K at different inputs all involving offset_a and L.
With enough blocks, we might be able to solve for offset_a and L.

But E_K is AES - nonlinear. The equations involve AES of linear combinations
of unknowns. This is essentially the same as breaking AES, which is infeasible.

CONCLUSION: Without recovering L* (which requires the short-nonce attack
blocked by the length check), we cannot break the scheme.

NEW IDEA: Use the SERVER's encrypt function as a black-box oracle.
Since we know plaintext and can observe ciphertext, maybe we can use
a CHOSEN-PLAINTEXT ATTACK to extract key material.

Actually: encrypt message A with chosen chunks -> get (N, C, T)
Encrypt message A AGAIN (same chunks) -> get (N', C', T')
The two ciphertexts are different (different nonces), but the plaintexts
are the same.

From repeated encryptions of the SAME message:
We observe: C_a[i], C_b[i], C_c[i], ... for the same P_i
All satisfy: C_x[i] = E_K(P_i ^ Delta_x[i]) ^ Delta_x[i]

If we collect MANY samples (337 queries), can we recover Delta values?
This is like a known-plaintext attack on AES in OCB mode.
With known plaintext and ciphertext but unknown tweak, this is hard.

WAIT: the first block P1 = "your beautiful p" is always the same.
For EVERY encryption (even different messages!), P1 is the same.

C_x[1] = E_K(P1 ^ (offset_x ^ L[0])) ^ (offset_x ^ L[0])

So the only difference between encryptions for block 1 is offset_x.
offset_x = E_K(nonce_block_x) (or shifted version).

So: C_x[1] = E_K(P1 ^ E_K(NB_x) ^ L[0]) ^ E_K(NB_x) ^ L[0]

This is E_K of E_K of something! Double encryption!

Hmm, but this doesn't help directly.

Let me try a completely different approach: brute-force the tag space
using the decrypt oracle with a SHORT tag. 

What if the tag length CHECK has an off-by-one? 
"""
import socket, json, random, struct
from collections import defaultdict

BLOCK_SIZE = 16

def xor(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

def pad10(partial):
    return partial + b"\x80" + b"\x00" * (16 - len(partial) - 1)

def checksum(pt):
    full = len(pt) // BLOCK_SIZE
    cs = b"\x00" * BLOCK_SIZE
    for i in range(full):
        cs = xor(cs, pt[i * BLOCK_SIZE : (i + 1) * BLOCK_SIZE])
    tail = pt[full * BLOCK_SIZE :]
    if tail:
        cs = xor(cs, pad10(tail))
    return cs

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(30)
    s.connect(("challenges.cybersecuritychallenge.pt", 26303))
    
    def recv():
        d = b""
        while True:
            c = s.recv(1)
            if not c or c == b"\n": break
            d += c
        return d.decode()
    def send(m): s.send((m + "\n").encode())
    
    chunks = [recv().strip() for _ in range(200)]
    print(f"[*] Got {len(chunks)} chunks")
    
    prefix = "your beautiful plaintext: "
    suffix = "!"
    P1 = b"your beautiful p"
    
    def plaintext(idxs):
        return (prefix + "".join(chunks[i] for i in idxs) + suffix).encode()
    
    # ============================================================
    # NEW APPROACH: Encrypt same message MANY TIMES.
    # The first block is always P1. The offset varies.
    # 
    # C_i[1] = E(P1 ^ offset_i ^ L0) ^ (offset_i ^ L0)
    # 
    # For EVERY pair of encryptions of the SAME message:
    # C_a[1] ^ C_b[1] = E(X_a) ^ E(X_b) ^ D_ab
    # T_a ^ T_b = E(Y_a) ^ E(Y_b)
    # where X_a = P1 ^ offset_a ^ L0
    #       Y_a = cs ^ offset_a ^ L_d (no L* in this code!)
    #       D_ab = offset_a ^ offset_b
    #
    # The tag uses L_dollar, NOT L*! So Y_a = cs ^ offset_a ^ L_dollar.
    # X_a = P1 ^ offset_a ^ L0 = P1 ^ offset_a ^ 4L* = P1 ^ offset_a ^ 2*L_d
    #
    # If cs ^ L_d = P1 ^ L0: Y_a = X_a (condition)
    #   cs ^ 2L = P1 ^ 4L
    #   cs = P1 ^ 6L
    #   L = (P1 ^ cs) / 6
    # ============================================================
    
    print("[*] Encrypting same message multiple times...")
    
    idxs = [0, 1, 2, 3]
    encs = []
    for _ in range(100):
        send("E " + " ".join(map(str, idxs)))
        resp = json.loads(recv())
        encs.append({
            "nonce": resp["nonce"],
            "ct": bytes.fromhex(resp["ciphertext"]),
            "tag": bytes.fromhex(resp["tag"]),
        })
    
    pt = plaintext(idxs)
    cs_val = checksum(pt)
    flag = 1 if len(pt) % BLOCK_SIZE > 0 else 0
    n_blocks = len(pt) // BLOCK_SIZE
    
    print(f"[*] {len(encs)} encryptions of same message")
    print(f"[*] Plaintext: {len(pt)} bytes, {n_blocks} blocks + {len(pt)%BLOCK_SIZE} tail")
    print(f"[*] Checksum: {cs_val.hex()}")
    
    # For each pair, compute D_candidate = C_a[1] ^ C_b[1] ^ T_a ^ T_b
    # If the condition holds: D_candidate = offset_a ^ offset_b
    # This D should be CONSISTENT across ALL block pairs!
    
    # Actually, for ANY pair: C_a[1] ^ C_b[1] ^ D = E(X_a) ^ E(X_b)
    #                              T_a ^ T_b = E(Y_a) ^ E(Y_b)
    # If X_a = Y_a: C_a[1] ^ C_b[1] ^ D = T_a ^ T_b
    # => D = C_a[1] ^ C_b[1] ^ T_a ^ T_b
    
    print("\n[*] Computing D candidates from first 10 pairs...")
    d_candidates = []
    for i in range(min(10, len(encs))):
        for j in range(i+1, min(10, len(encs))):
            ca1 = encs[i]["ct"][:16]
            cb1 = encs[j]["ct"][:16]
            ta = encs[i]["tag"]
            tb = encs[j]["tag"]
            d = xor(xor(ca1, cb1), xor(ta, tb))
            d_candidates.append(d)
    
    # These D values should all be equal if condition holds.
    # Check if any two D values match
    for i in range(len(d_candidates)):
        for j in range(i+1, len(d_candidates)):
            if d_candidates[i] == d_candidates[j]:
                print(f"  MATCH! D[{i}] == D[{j}] = {d_candidates[i].hex()}")
    
    # Also: if condition holds, for each encrypt:
    # Delta_1 = C_1 ^ T = offset ^ L0
    # offset = Delta_1 ^ L0
    # And L* = (P1 ^ cs ^ flag) / 6
    
    # Let's compute L* candidates for each encrypt
    print("\n[*] Computing L* candidates...")
    
    # In GF(2^128): L* = (P1 ^ cs ^ flag) * inv(6)
    # First compute inv(6)
    mod = (1 << 128) | 0x87
    def gf_inv(a):
        r0, r1 = mod, a
        t0, t1 = 0, 1
        while r1:
            shift = r0.bit_length() - r1.bit_length()
            if shift >= 0:
                r0 ^= r1 << shift
                t0 ^= t1 << shift
            if r0 == 0:
                break
            r0, r1 = r1, r0
            t0, t1 = t1, t0
        while t1.bit_length() > 128:
            t1 ^= mod << (t1.bit_length() - 129)
        return t1
    
    inv6 = gf_inv(6)
    print(f"[*] inv(6) = {inv6:#034x}")
    
    # For each encrypt: L* = (P1 ^ cs ^ flag) * inv6
    val = int.from_bytes(P1, "big") ^ int.from_bytes(cs_val, "big") ^ flag
    # Multiply val by inv6 in GF(2^128)
    lstar_int = 0
    v = val
    i = inv6
    while i:
        if i & 1:
            lstar_int ^= v
        carry = v >> 127
        v = (v << 1) & ((1 << 128) - 1)
        if carry:
            v ^= 0x87
        i >>= 1
    
    Lstar_candidate = lstar_int.to_bytes(16, "big")
    print(f"[*] L* candidate = {Lstar_candidate.hex()}")
    
    # Compute Delta_1 for each encrypt
    print("\n[*] Computing Delta_1 = C_1 ^ T for each encrypt:")
    for i in range(min(5, len(encs))):
        delta1 = xor(encs[i]["ct"][:16], encs[i]["tag"])
        print(f"  [{i}] Delta_1 = {delta1.hex()}")
    
    # If condition holds: Delta_1 = offset ^ L0
    # offset = Delta_1 ^ L0
    # L0 = 4*L* (checked via double_block twice)
    # offset should be: E_K(nonce_block) for the encrypt's nonce
    
    # We can't verify without knowing E_K.
    # But we CAN check: is offset consistent between encrypts?
    # For encrypts i and j: offset_i ^ offset_j = Delta_1[i] ^ Delta_1[j]
    # This should equal D from the ciphertext calculation!
    
    # Let's verify: for the first two encrypts
    if len(encs) >= 2:
        d1_a = xor(encs[0]["ct"][:16], encs[0]["tag"])
        d1_b = xor(encs[1]["ct"][:16], encs[1]["tag"])
        d_delta = xor(d1_a, d1_b)
        
        ca1 = encs[0]["ct"][:16]
        cb1 = encs[1]["ct"][:16]
        ta = encs[0]["tag"]
        tb = encs[1]["tag"]
        d_ct_tag = xor(xor(ca1, cb1), xor(ta, tb))
        
        print(f"\n[*] Consistency check:")
        print(f"  Delta_1[a] ^ Delta_1[b] = {d_delta.hex()}")
        print(f"  C_a[1]^C_b[1]^T_a^T_b = {d_ct_tag.hex()}")
        print(f"  Match: {d_delta == d_ct_tag}")
        # These are mathematically equal regardless of condition!
    
    # ============================================================
    # THE ACTUAL ATTACK:
    # Since we can't recover L* from short nonces, and the condition
    # has prob 2^(-128), let's try a DIFFERENT approach.
    #
    # What if we can FORGE by modifying the TAIL and using the
    # SAME tag from another encryption?
    #
    # Encrypt message A with indices [0,1,2,3] -> (Na, Ca, Ta)
    # We want to forge for indices [4,5,6,7] -> need (Nb, Cb, Tb)
    #
    # Ca and Cb share the same first block (P1). For other blocks,
    # they differ. We can't compute new blocks without the key.
    #
    # BUT: what if we use the DECRYPT oracle to brute-force
    # a 1-byte modification?
    #
    # If we flip the last byte of the tail ciphertext, the tail
    # changes from 'x' to 'y'. The checksum changes by a known delta.
    # If we can find a tag that works for the new checksum, we win.
    #
    # But the tag is 128 bits. Can't brute-force.
    #
    # HOWEVER: what if the checksum change is ZERO?
    # That requires pad_10star(x) = pad_10star(y) => x = y.
    # No change possible.
    # ============================================================
    
    # Let me try: encrypt message B, then use its tag with message A's
    # ciphertext blocks, but RECONSTRUCT the ciphertext using known
    # plaintext-ciphertext pairs from the SAME nonce (which we can't get)
    
    # Actually, what if I encrypt BOTH messages and use the XOR
    # of ciphertexts to derive the tag?
    
    print("\n[*] Encrypting second message for comparison...")
    idxs2 = [4, 5, 6, 7]
    pt2 = plaintext(idxs2)
    cs2 = checksum(pt2)
    
    send("E " + " ".join(map(str, idxs2)))
    resp2 = json.loads(recv())
    
    print(f"[*] Message B: {len(pt2)} bytes, cs={cs2.hex()}")
    print(f"[*] Block structures: A({n_blocks}f+{len(pt)%16}t) B({len(pt2)//16}f+{len(pt2)%16}t)")
    
    # Check if same block structure
    if n_blocks == len(pt2) // BLOCK_SIZE and len(pt) % BLOCK_SIZE == len(pt2) % BLOCK_SIZE:
        print("[*] Same block structure! Checksums may be comparable.")
        
        # Show which blocks match
        for b in range(n_blocks):
            ba = pt[b*16:(b+1)*16]
            bb = pt2[b*16:(b+1)*16]
            if ba == bb:
                print(f"  Block {b}: MATCH")
            else:
                print(f"  Block {b}: differ")
    
    s.close()
    print("\n[*] Done. No flag found with these approaches.")

if __name__ == "__main__":
    main()
