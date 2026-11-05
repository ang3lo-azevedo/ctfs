#!/usr/bin/env python3

import os
import json
from utils import NotOCB3
import string
import random

flag = os.getenv('FLAG', 'TeamItaly{redacted}')
alph = string.ascii_letters
key = os.urandom(16)

chunks = [os.urandom(random.randint(1, 16)).hex() for _ in range(200)]
seen = []
prefix = "your beautiful plaintext: "
suffix = "!"

for chunk in chunks:
    print(chunk)
    
for _ in range(337):
    query = input()
    idxs = list(map(int, query.split()[1:]))
    assert all(0 <= idx < len(chunks) for idx in idxs)
    assert len(idxs) > 3 and len(set(idxs)) == len(idxs)
    if query[0] == 'E':
        nonce = os.urandom(8)
        plaintext = prefix + "".join([chunks[idx] for idx in idxs]) + suffix
        aad = b""
        ciphertext, tag = NotOCB3(key).encrypt(nonce, plaintext.encode(), aad)
        print(json.dumps({
            'nonce': nonce.hex(),
            'ciphertext': ciphertext.hex(),
            'tag': tag.hex(),
        }))
        seen.append(plaintext)
    elif query[0] == 'D':
        nonce = bytes.fromhex(input())
        ciphertext = bytes.fromhex(input())
        tag = bytes.fromhex(input())
        aad = b""
        try:
            expected = prefix + "".join([chunks[idx] for idx in idxs]) + suffix
            plaintext = NotOCB3(key).decrypt(nonce, ciphertext, tag, aad).decode()
            if plaintext == expected  and plaintext not in seen:
                print("gg")
                break
            else:
                print(json.dumps({
                    'plaintext': plaintext,
                    'expected': expected,
                }))
        except Exception as e:
            print(json.dumps({
                'error': str(e),
            }))
else:
    exit(1)

print("flag =", flag)
