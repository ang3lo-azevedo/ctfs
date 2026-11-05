#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

def rc4(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    
    x = 0
    y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + S[x]) % 256
        S[x], S[y] = S[y], S[x]
        out.append(char ^ S[(S[x] + S[y]) % 256])
        
    return bytes(out)

def main():
    label = b"CSCPT26"
    cfg = bytes.fromhex("13 37 be ef")
    dkey = bytearray()
    for i in range(len(label)):
        dkey.append(label[i] ^ cfg[i % len(cfg)])
        
    print(f"Key: {dkey.hex()}")
    
    with open("4840010456e212cebd111fef50f02c4ec720db7daaf9554044dc7306f1bd665b/secret.enc", "rb") as f:
        enc = f.read()
        
    dec = rc4(dkey, enc)
    print("Decrypted:", dec)
    
if __name__ == "__main__":
    main()