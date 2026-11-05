#!/usr/bin/env python3
import re

def main():
    with open('lincense_c', 'r') as f:
        content = f.read()

    matches = re.findall(r'rax_(\d+) [!=]= (0x[0-9a-f]+)', content)
    
    chars = {}
    for idx, val in matches:
        v = int(val, 16)
        if 0x20 <= v <= 0x7e:
            chars[int(idx)] = v
        
    if not chars:
        print("No characters found!")
        return
        
    max_idx = max(chars.keys())
    
    key = ""
    for i in range(1, max_idx + 1):
        if i in chars:
            key += chr(chars[i])
        else:
            key += "?"
            
    print("Extracted Key:", key)
    with open('license.lic', 'w') as f:
        f.write(key)

if __name__ == "__main__":
    main()