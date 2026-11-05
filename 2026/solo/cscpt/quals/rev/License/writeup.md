---
title: License
date: '2026-06-20'
draft: false
authors: ['ang3lo']
tags: ['Reverse Engineering', 'Scripting', 'Regex']
summary: 'Extracting a license key from a massive decompiled C file using a custom Python parsing script.'
canonical: ''
---

## License

## Table of Contents

1. [Source](#Source)
2. [Solution](#Solution)

## Main Content

### Source
The challenge provides a massive decompiled C file `lincense_c` (almost 9MB) and a statically linked ELF executable `license`. Running the binary indicates that it expects a `license.lic` file.

### Solution

By exploring the `lincense_c` file, we can locate the main license-checking function, `sub_401685`. The function opens `license.lic` and checks the characters of the file byte-by-byte using `_IO_getc`. The character verifications are implemented as individual checks against hexadecimal values, formatted like:

```c
if (rax_2 == 0x6b)
...
if (rax_3 != 0x65)
```

Due to the file's immense size, matching each character manually would be too tedious. However, we can use a Python script with Regex to extract the expected hexadecimal values and reconstruct the license key. We restrict the search to the boundaries of the `sub_401685` function to avoid extracting noise from other functions or variables.

```python
#!/usr/bin/env python3
import re

def main():
    with open('lincense_c', 'r') as f:
        content = f.read()

    # Search within the validation function boundaries
    start = content.find('sub_401685')
    end = content.find('sub_401bca', start)
    
    matches = re.findall(r'rax_(\d+) [!=]= (0x[0-9a-f]+)', content[start:end])
    
    chars = {}
    for idx, val in matches:
        v = int(val, 16)
        # Ensure we only pick valid ASCII characters
        if 0x20 <= v <= 0x7e:
            chars[int(idx)] = v
            
    max_idx = max(chars.keys())
    
    key = ""
    for i in range(1, max_idx + 1):
        if i in chars:
            key += chr(chars[i])
            
    print("Extracted Key:", key)
    with open('license.lic', 'w') as f:
        f.write(key)

if __name__ == "__main__":
    main()
```

Running the script extracts the correct characters, outputs them to our file, and reveals the valid license key:
`{key:b4f59ac919658715538a7b20f4204a219b98c34b}`

We can then supply this `license.lic` to the binary to reveal our flag!

```bash
$ ./license
License valid! Flag: CSCPT{52197b3a430dda2020c61bcf5fd88eb1f02c4c3e1c1133e1f83c124514e85c96}
```