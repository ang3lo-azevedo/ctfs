---
title: ECsC — Singular Curve Invalid Point Attack
date: '2026-06-20'
draft: false
authors: ['player']
tags: ['crypto', 'ECC', 'invalid-curve', 'singular']
summary: 'Binary search on singular curve of order 2^127 to recover secret bit-by-bit.'
canonical: ''
---

## ECsC

### Challenge Overview

The server implements an elliptic curve oracle over F_p with p = 2^127 - 1 (Mersenne prime), a = p - 3, and a given b. It accepts any `(x, y)` point, multiplies it by a secret scalar, and returns an HMAC of the result. The flag is encrypted with SHA256(secret).

### Vulnerability

1. **No point validation**: The server does not check that submitted points are on the actual curve.
2. **Mersenne prime**: p = 2^127 - 1, so p + 1 = 2^127.
3. **Singular curve**: For b = 2, the discriminant Δ = 4a³ + 27b² = 0 (mod p). The curve y² = x³ + ax + 2 = (x-1)²(x+2) is singular with a node at (1, 0). The nonsingular points form a cyclic group of order p + 1 = 2^127.

### Attack: Singular Curve Binary Search

Since the group order is a power of 2, we recover the secret bit-by-bit:

1. Find a generator P of the singular curve group (order 2^127). Verify 2^126·P ≠ O.
2. Precompute Q_i = 2^i·P for i = 0..126. Q_i has order 2^(127-i).
3. For i from 126 down to 0:
   - Query GET Q_i → get MAC(secret·Q_i)
   - Since secret·Q_i depends only on secret mod 2^(127-i), and we know
     secret mod 2^(bits_known), there are only 2 candidates for the next bit
   - Compute MAC for both candidates, compare → recover one more bit
4. After 127 queries, full 127-bit secret is known.
5. Decrypt flag with keystream keyed by SHA256(str(secret)).

### Flag

```
CSCPT{please_perform_all_the_checks_otherwise_we_have_invalid_point_attack_FTW}
```
