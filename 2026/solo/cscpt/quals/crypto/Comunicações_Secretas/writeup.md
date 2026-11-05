---
title: Comunicações Secretas
date: '2026-06-20'
draft: false
authors: ['Antigravity']
tags: ['Crypto', 'AES-CTR', 'Many-Time Pad', 'Crib Dragging']
summary: 'Exploiting a Many-Time Pad vulnerability in AES-CTR where the nonce and key are identical across multiple ciphertexts, enabling crib dragging and heuristic keystream recovery to extract the flag.'
canonical: ''
---

## Comunicações Secretas

## Table of Contents

1. [Source](#Source)
2. [Solution](#Solution)

## Source
The challenge involves a custom secure messaging system designed to send messages to the "captain" (Cristiano Ronaldo). We are provided with a Python script `challenge.py` that demonstrates how the messages are encrypted and a file `ciphertexts.txt` containing multiple base64-encoded ciphertexts.

The core of the encryption logic in `challenge.py` is as follows:
```python
cipher = AES.new(KEY, AES.MODE_CTR, nonce=NONCE)
```
Crucially, both the `KEY` and `NONCE` are constant for all encryptions:
```python
NONCE = hashlib.sha256(KEY).hexdigest()[:16].encode()
```

## Solution

Because AES-CTR operates essentially as a stream cipher, it XORs the plaintext with a keystream generated from the key and nonce. When the exact same key and nonce are reused across multiple messages, the keystream is identical for every encryption. This is a classic **Many-Time Pad** vulnerability.

The vulnerability allows us to XOR any two ciphertexts together, which cancels out the keystream and yields the XOR of the two plaintexts:
`C1 ⊕ C2 = P1 ⊕ P2`

With 9 ciphertexts available, we can apply "crib dragging" — guessing common words or phrases in one message and observing the effect on the other messages.

### Analysis & Crib Dragging
1. We know the constraints:
   - The messages are primarily in Portuguese, giving support to Cristiano Ronaldo.
   - We are explicitly told by the script constraints that all normal messages contain the string `"Cristiano Ronaldo"`.
   - The flag is stored in one of the messages and is exactly 48 bytes long, starting with `CSCPT{`.

2. By analyzing the ciphertext lengths and dragging `"Cristiano Ronaldo"` and common Portuguese phrases (like "Capitao", "Portugal", "orgulho", "dedicacao"), we were able to recover significant portions of the plaintexts.

3. We found that the flag resides in CT 4 starting at offset 101. The prefix `CSCPT{` at offset 101 gave us the first 6 bytes of the keystream for those positions.

### Heuristic Keystream Recovery
Since the flag spans offsets 101 to 148, we needed to recover the keystream for that specific region. To automate this, we wrote a heuristic script that evaluated all 256 possible bytes for the keystream at each position. 

The script assigned points when the resulting decrypted byte for the other ciphertexts (CT 1, 2, 3, 5, 6, 7, 8) produced:
- Valid printable characters (letters, numbers, common punctuation, and spaces)
- Common vowels (`a, e, i, o, u`)
- Common Portuguese consonants (`s, r, t, d, n, m, l, c`)

Using this heuristic scoring, the script yielded a highly readable flag:
`CSCPT{You_ShoUld_never_reuSe_zonces_in_kirxxoC0k`

### Final Refinement
With the near-perfect string in hand, we manually corrected the typos (e.g., `ShoUld` to `Should`, `zonces` to `nonces`) and guessed the context-appropriate ending. Given the cryptographic flaw involved reusing nonces in CTR mode, the final words were predictably `CTR_mode}`.

Testing this final string verified that it perfectly decrypted the tails of the other Portuguese messages:
- CT 1: `e amor pelA camisola.`
- CT 2: ` vive no cOracao de todo Portugal.`
- CT 6: `nua a levaNtar todo Portugal.`

The recovered flag is:
**`CSCPT{You_Should_never_reuse_nonces_in_CTR_mode}`**