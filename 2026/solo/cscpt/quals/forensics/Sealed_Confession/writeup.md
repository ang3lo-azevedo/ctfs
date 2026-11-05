---
title: "Sealed Confession"
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['Forensics', 'DPAPI', 'Windows', 'KAPE', 'Credential Manager']
summary: 'Decrypting Windows DPAPI-protected Credential Manager vault by cracking the user password from SAM hashes'
canonical: ''
---

## Sealed Confession

> A workstation was triaged during an incident response. The user swore they never wrote anything sensitive down. Windows disagreed.

**Category**: Forensics  
**Points**: 500

## Table of Contents

1. [Source](#Source)
2. [Solution](#Solution)
3. [Flag](#Flag)
4. [Tools Used](#Tools-Used)

## Source

The challenge provides a ZIP file containing KAPE triage artifacts from a Windows workstation. The collection includes:

- **Registry Hives**: SAM, SYSTEM, SECURITY, SOFTWARE, NTUSER.DAT (users `cscpt`, `user`, `Default`)
- **DPAPI Artifacts**: 
  - `S-1-5-21-...-1002\57ee3ee0-3f04-4f0e-a9c9-401277f426f5` - Master key
  - `Vault\3E0E35BE-...\blob.dpapi` - Encrypted Credential Manager vault
  - `S-1-5-18\*` - SYSTEM account DPAPI keys
- **Windows Search Index**, **Prefetch**, **Thumbcache**, **Jump Lists**

## Solution

### 1. Extract Password Hashes

Use `pypykatz` to dump SAM hashes:

```bash
pypykatz registry SYSTEM --sam SAM --security SECURITY
```

```
user:1001  LM:aad3b435b51404ee  NT:91f5d0b4fae63bcab6132ddaa23a5b5e
cscpt:1002 LM:aad3b435b51404ee  NT:91f5d0b4fae63bcab6132ddaa23a5b5e
```

Both accounts share the same NT hash. LSA DPAPI secrets also extracted for SYSTEM key decryption.

### 2. Crack the NT Hash

The NT hash `91f5d0b4fae63bcab6132ddaa23a5b5e` cracks to the password:

```
QwertY123
```

### 3. Decrypt the DPAPI Master Key

Using `dpapick3`, decrypt the cscpt user's master key with the recovered password and SID:

```python
from dpapick3 import masterkey

mk = masterkey.MasterKeyFile(raw_masterkey)
mk.decryptWithPassword('S-1-5-21-1584158716-3183168098-2233993493-1002', 'QwertY123')
# True - master key: bb3e3c9565a9a013...
```

### 4. Decrypt the Vault Blob

Use the decrypted master key to decrypt the Credential Manager vault blob:

```python
from dpapick3 import blob as dpapi_blob

b = dpapi_blob.DPAPIBlob(raw_vault)
b.decrypt(master_key_bytes)
# True - reveals the stored credential
```

### 5. Windows AutoLogon Context

The SOFTWARE registry hive confirmed AutoLogon was configured for the `cscpt` user:

```
AutoAdminLogon = 1
DefaultUserName = cscpt
DefaultDomainName = .
AutoLogonCount = 1
```

The `DefaultPassword` LSA secret was deleted after the one-time AutoLogon consumed it, but traces remain in `SECURITY.LOG1`. The `SECURITY.LOG1` at offset `0x32d4` also contained a cached credential blob with the NT hash and username.

## Flag

```
CSCPT{c6d3bab555c0ead5ad07cdd6e44d64f6fc325eb2befb62f57d32a8e04952fa2f}
```

## Tools Used

- **pypykatz** - SAM/LSA parsing, DPAPI SYSTEM key decryption
- **dpapick3** - Python DPAPI master key + blob decryption
- **hashcat** / online lookup - NT hash cracking (`QwertY123`)
- **7-Zip** - Extracting Deflate64-compressed ZIP
- **python-registry** - Registry hive inspection
- **esedbexport** (libesedb-utils) - ESE database export
