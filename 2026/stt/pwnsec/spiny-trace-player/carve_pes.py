import pefile

with open('decrypted_captcha.bin', 'rb') as f:
    data = f.read()

# Find all MZ headers (Windows PE Signature)
mz_indices = [i for i in range(len(data)) if data.startswith(b'MZ', i)]

for idx in mz_indices:
    if idx == 0:
        continue # Skip the main payload itself
    
    print(f"\n[+] Found embedded MZ header at offset {hex(idx)}!")
    try:
        pe = pefile.PE(data=data[idx:])
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            print(f"    Export Name: {pe.DIRECTORY_ENTRY_EXPORT.name.decode('utf-8')}")
        else:
            print("    [-] No Export Name found in embedded PE.")
    except Exception as e:
        print(f"    [-] Could not parse embedded PE: {e}")