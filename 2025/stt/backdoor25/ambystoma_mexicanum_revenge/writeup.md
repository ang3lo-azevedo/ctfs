# Ambystoma Mexicanum Revenge - Writeup (IN PROGRESS)

**Challenge:** Ambystoma Mexicanum Revenge  
**Category:** Crypto  
**Points:** 499  
**Author:** Entity069  
**Status:** 🔴 UNSOLVED

## Description

> The axolotls are not what they seem, they are back now, with a revenge.
> 
> `nc remote.infoseciitr.in 4005`

## Analysis

This is a sequel to the original "Ambystoma Mexicanum" challenge. The service uses AES-GCM-SIV encryption with the following key difference:

**Original code (line 90):**
```python
key = binascii.unhexlify(KEYS[i % len(KEYS)])
```

**Revenge code (line 90):**
```python
key = binascii.unhexlify(KEYS[i])
```

### Key Differences

In the original challenge:
- You could keep just 1 key
- The modulo operation `i % len(KEYS)` meant the same key was reused for all 4 iterations
- Solution: Encrypt a 64-byte message with that single key, where each 16-byte chunk contains the appropriate part of "gib me flag plis"

In the revenge challenge:
- The code directly accesses `KEYS[i]`, meaning it needs `KEYS[0]`, `KEYS[1]`, `KEYS[2]`, `KEYS[3]`
- You must rotate keys 3 times to have 4 keys (or you get IndexError)
- The flag request loop uses the SAME ciphertext but DIFFERENT keys:
  ```python
  for i in range(4):
      key = binascii.unhexlify(KEYS[i])  # Different key each iteration!
      ct = binascii.unhexlify(CIPHERTEXTS[i % len(CIPHERTEXTS)])  # Same CT
      text = service.decrypt(ct, key)[16 * i:16 * (i+1)].decode('utf-8').strip()
  ```

### The Problem

The challenge requires:
1. ONE ciphertext (limited by `CIPHERTEXTS_LEN = 1`)
2. That ciphertext must successfully decrypt with FOUR different random keys
3. Each decryption must produce the correct 16-byte chunk at the right position

With authenticated encryption (AES-GCM-SIV):
- A ciphertext can only decrypt successfully with the correct key
- Wrong key → authentication failure → decrypt() returns None → exception → exit
- Finding a ciphertext that validates with multiple random keys is cryptographically infeasible

## Attempted Approaches

### 1. Encrypt with Single Key (Original Solution)
```python
# Use first key only, don't rotate
plaintext = b"gib m           e fl            ag p            lis             "
ct = AESGCMSIV(keys[0]).encrypt(nonce, plaintext, b"")
```
**Result:** ❌ Fails - decryption with keys[1], keys[2], keys[3] fails authentication

### 2. Encrypt with Each Key Individually
Tried encrypting the plaintext with each of the 4 keys separately.
**Result:** ❌ All fail - same issue, wrong keys can't decrypt

### 3. Multi-layer Encryption
Tried encrypting with all 4 keys in sequence (nested encryption).
**Result:** ❌ Doesn't help - still can't decrypt with individual keys

### 4. Multiple Ciphertexts
Attempted to push 4 different ciphertexts.
**Result:** ❌ Server limits to 1 ciphertext, breaks loop after 2nd push

### 5. Key Relationship Exploitation
Checked if keys have mathematical relationships (XOR, patterns, etc.).
**Result:** ❌ Keys are random, no exploitable relationship found

### 6. Edge Cases & Bypasses
- Empty ciphertext list → crashes
- No key rotation → IndexError when accessing KEYS[1]
- Code injection through hex input → not possible
- Out-of-bounds slicing → produces empty string → fails check

### 7. Server vs Local Code Mismatch
Tested if server might be running original code instead of revenge code.
**Result:** ❌ Server confirmed running revenge version

## Theoretical Possibilities

Since the challenge appears solvable (it's worth 499 points), the solution likely involves:

1. **Hidden vulnerability** in the specific version of `cryptography` library
2. **Server configuration** where `CIPHERTEXTS_LEN != 1` (allows multiple CTs)
3. **Non-cryptographic exploit** (buffer overflow, race condition, etc.)
4. **Mathematical weakness** in how AES-GCM-SIV is implemented for this specific use case
5. **Missing information** - perhaps there's an additional file or hint
6. **Challenge is actually broken** (unlikely but possible)

## Files

- `chall.py` - Challenge source code
- `solve*.py` - Various solution attempts
- `test_*.py` - Testing scripts for different approaches

## Verified Facts

✅ Server has `CIPHERTEXTS_LEN = 1` (confirmed by testing - breaks after pushing 2nd CT)
✅ Server uses `KEYS[i]` not `KEYS[i % len(KEYS)]` (confirmed - original solution fails)
✅ Server requires 4 different keys (must rotate 3 times or get IndexError)
✅ AES-GCM-SIV decryption with wrong key raises `cryptography.exceptions.InvalidTag`
✅ No input injection possible through hex string
✅ Keys are cryptographically random (os.urandom)
✅ One ciphertext must work with all 4 different keys - **CRYPTOGRAPHICALLY IMPOSSIBLE**

## Next Steps

- [ ] Check for known vulnerabilities in specific cryptography library version
- [ ] Investigate if CTF platform has updated challenge files
- [ ] Look for official hints or community discussion
- [ ] Contact challenge author for clarification
- [ ] Consider if challenge is actually solvable as-is

## Notes

The challenge description says "The axolotls are not what they seem" - this suggests deception or a trick. The solution likely involves thinking outside the box rather than pure cryptography.

---

**Last Updated:** December 6, 2025  
**Time Spent:** ~2 hours  
**Status:** Investigating alternative approaches
