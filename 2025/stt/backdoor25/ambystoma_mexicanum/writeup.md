# Ambystoma Mexicanum - Writeup

**Challenge:** Ambystoma Mexicanum  
**Category:** Crypto  
**Points:** 100  
**Author:** Entity069

## Description

The axolotl (Ambystoma mexicanum) is a species of paedomorphic mole salamander, meaning they mature without undergoing metamorphosis into the terrestrial adult form; the adults remain fully aquatic with obvious external gills.

`nc remote.infoseciitr.in 4004`

## Analysis

The challenge provides a cryptographic service that uses AES-GCM-SIV encryption. Looking at the code:

1. The service initializes with a random key and nonce
2. We can:
   - Rotate keys (generate new keys)
   - Debug (view keys, ciphertexts, and nonce)
   - Push a ciphertext (limited to 1)
   - Request the flag

To get the flag, we need to provide a ciphertext that when decrypted produces the message `"gib me flag plis"`.

The key vulnerability is in the flag request logic:
```python
for i in range(4):
    key = binascii.unhexlify(KEYS[i % len(KEYS)])
    ct = binascii.unhexlify(CIPHERTEXTS[i % len(CIPHERTEXTS)])
    text = service.decrypt(ct, key)[16 * i:16 * (i+1)].decode('utf-8').strip()
    usertext += text
```

The service:
1. Uses the same ciphertext for all 4 iterations
2. Cycles through available keys (keys[i % len(KEYS)])
3. Takes different 16-byte slices from the decrypted plaintext
4. Strips whitespace and concatenates them

## Solution

The trick is to NOT rotate keys, so we only have 1 key. This means all 4 decryptions use the same key, giving us the same plaintext each time.

We need to:
1. Split "gib me flag plis" (16 chars) into 4 parts that don't end with spaces (to survive .strip()):
   - Chunk 0: "gib m" 
   - Chunk 1: "e fl"
   - Chunk 2: "ag p"
   - Chunk 3: "lis"

2. Create a 64-byte plaintext where each chunk is padded to 16 bytes
3. Encrypt it with the service's key and nonce
4. Submit this ciphertext

When decrypted:
- Iteration 0: bytes[0:16] = "gib m" (after strip)
- Iteration 1: bytes[16:32] = "e fl" (after strip)
- Iteration 2: bytes[32:48] = "ag p" (after strip)
- Iteration 3: bytes[48:64] = "lis" (after strip)
- Concatenated: "gib me flag plis" ✓

## Flag

`flag{th3_4x0lo7ls_4r3_n07_wh47_th3y_s33m}`
