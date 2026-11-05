#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sealed Confession - CSCPT 2026 Quals Forensics Challenge

A workstation was triaged during an incident response. The user swore they 
never wrote anything sensitive down. Windows disagreed.

Solution:
1. Extract DPAPI artifacts from KAPE collection
2. Parse SAM/SYSTEM/SECURITY registry hives to get user hashes & LSA keys
3. Extract NT hashes: both user and cscpt share 91f5d0b4fae63bcab6132ddaa23a5b5e
4. Crack the NT hash to get password: QwertY123
5. Decrypt cscpt DPAPI master key with password + SID
6. Decrypt Vault blob (Credential Manager) with master key
7. Extract flag
"""

import sys
from dpapick3 import masterkey, blob as dpapi_blob

# Paths
MK_PATH = 'C/Users/cscpt/AppData/Roaming/Microsoft/Protect/S-1-5-21-1584158716-3183168098-2233993493-1002/57ee3ee0-3f04-4f0e-a9c9-401277f426f5'
VAULT_PATH = 'C/Users/cscpt/AppData/Roaming/Microsoft/Vault/3E0E35BE-1B77-43E7-B873-AED901B6275B/blob.dpapi'

# Credentials recovered from SAM + hash cracking
SID = 'S-1-5-21-1584158716-3183168098-2233993493-1002'
PASSWORD = 'QwertY123'

def main():
    # Step 1: Decrypt cscpt master key
    with open(MK_PATH, 'rb') as f:
        mk_raw = f.read()
    
    mk = masterkey.MasterKeyFile(mk_raw)
    mk.decryptWithPassword(SID, PASSWORD)
    
    if not mk.decrypted:
        print("Failed to decrypt master key!")
        return 1
    
    cscpt_mk = mk.get_key()
    print(f"[+] Master key decrypted: {cscpt_mk.hex()}")
    
    # Step 2: Decrypt vault blob
    with open(VAULT_PATH, 'rb') as f:
        vault_raw = f.read()
    
    dpapi_blob_obj = dpapi_blob.DPAPIBlob(vault_raw)
    dpapi_blob_obj.decrypt(cscpt_mk)
    
    if not dpapi_blob_obj.decrypted:
        print("Failed to decrypt vault blob!")
        return 1
    
    # Step 3: Extract flag
    flag = dpapi_blob_obj.cleartext.decode('ascii')
    print(f"\n[+] Flag: {flag}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
