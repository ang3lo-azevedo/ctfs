# Hidden in Plain Stream - CSCPT 2026 Quals (Forensics)

**Flag:** `CSCPT{66a2112700a0886fedd6811923a4e93ad328882a25a0b6b4c35fe4fdf2e731a3}`

## Challenge Description

A workstation was imaged after a "system maintenance helper" script was found running. The script is still on the disk, along with an encrypted file it produced. Recover the secret.

## Solution

### Step 1: Initial Triage

The challenge provides a raw disk image `cscpt26.dd`. Using `mmls` (from The Sleuth Kit) we identify a single NTFS partition at offset 128:

```
$ mmls cscpt26.dd
DOS Partition Table
      Slot      Start        End          Length       Description
002:  000:000   0000000128   0000202751   0000202624   NTFS / exFAT (0x07)
```

`fsstat -o 128` confirms NTFS with volume name `CSCPT26`.

### Step 2: File Listing and Extraction

Using `testdisk cscpt26.dd` we can interactively navigate the filesystem. Exploring the single NTFS partition, TestDisk conveniently displays Alternate Data Streams (ADS) alongside regular files. We can see and extract the following:

- **`totallylegit.vbs`** - The malicious script (poses as a Project Gutenberg text)
- **`totallylegit.vbs:cfg`** - An Alternate Data Stream (ADS) attached to the script
- **`secret.enc`** - The encrypted file produced by the script
- Deleted temp files (zeroed out, unrecoverable)

The challenge title "Hidden in **Plain Stream**" directly hints at NTFS Alternate Data Streams.

### Step 3: Extracting the ADS

The `:cfg` ADS contains exactly 4 bytes:

```sh
$ icat -o 128 cscpt26.dd 38-128-4 | xxd
00000000: 1337 beef                                .7..
```

Value: `13 37 be ef`

### Step 4: Deobfuscating the VBS Script

The VBS file is 3.5 MB of UTF-16LE encoded text - the entire Project Gutenberg eBook "On War" by Clausewitz, formatted as VBS comments (lines starting with `'`). The actual malicious code is embedded at the top and bottom, mixed within the first non-comment lines:

```vbs
Option Explicit
Dim fso, cfg, label, dkey, i, drv, plain
Set fso = CreateObject("Scripting.FileSystemObject")
cfg = ReadBytes(WScript.ScriptFullName & ":cfg")        ' Read the ADS
Set drv = fso.GetDrive(fso.GetDriveName(WScript.ScriptFullName))
label = drv.VolumeName                                   ' Get volume label
dkey = ""
For i = 1 To Len(label)
    dkey = dkey & Chr(Asc(Mid(label, i, 1)) Xor _
              Asc(Mid(cfg, ((i - 1) Mod Len(cfg)) + 1, 1)))  ' XOR key derivation
Next
plain = ReadText("X:\secret.txt")
WriteBytes "X:\secret.enc", RC4(dkey, plain)             ' RC4 encrypt
Shred "X:\secret.txt"                                    ' Wipe original
```

The script also contains full RC4 implementation and helper functions (`ReadBytes`, `ReadText`, `WriteBytes`, `Shred`).

### Step 5: Key Derivation

The encryption key is derived by XORing each character of the volume label with the `:cfg` bytes cyclically:

| Label char | Hex  | cfg byte | Hex  | XOR result | Hex  |
|------------|------|----------|------|------------|------|
| `C`        | 0x43 | `\x13`   | 0x13 | `P`        | 0x50 |
| `S`        | 0x53 | `\x37`   | 0x37 | `d`        | 0x64 |
| `C`        | 0x43 | `\xBE`   | 0xBE | `\xFD`     | 0xFD |
| `P`        | 0x50 | `\xEF`   | 0xEF | `\xBF`     | 0xBF |
| `T`        | 0x54 | `\x13`   | 0x13 | `G`        | 0x47 |
| `2`        | 0x32 | `\x37`   | 0x37 | `\x05`     | 0x05 |
| `6`        | 0x36 | `\xBE`   | 0xBE | `\x88`     | 0x88 |

**Derived key:** `5064fdbf470588`

### Step 6: RC4 Decryption

Using the derived key with RC4 on `secret.enc` (71 bytes) yields the flag.

### Decryption Script

```python
cfg = bytes([0x13, 0x37, 0xbe, 0xef])
label = 'CSCPT26'

# Derive key
key = bytes(ord(c) ^ cfg[i % len(cfg)] for i, c in enumerate(label))

# RC4
def rc4(key, data):
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    x = y = 0
    out = []
    for b in data:
        x = (x + 1) % 256
        y = (y + S[x]) % 256
        S[x], S[y] = S[y], S[x]
        out.append(b ^ S[(S[x] + S[y]) % 256])
    return bytes(out)

with open('secret.enc', 'rb') as f:
    print(rc4(key, f.read()).decode())
```
