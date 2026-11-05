#!/usr/bin/env python3

# Read the memory card file
with open('card.mcd', 'rb') as f:
    data = f.read()

# Find GT13 offset
offset = data.find(b'GT13')
print(f"GT13 found at offset: 0x{offset:x}")

# Extract the data after GT13 header
start = offset + 8  # Skip "GT13" and some header bytes
encrypted_data = data[start:start+88]

print(f"\nEncrypted data ({len(encrypted_data)} bytes):")
print(encrypted_data.hex())

# Try simple XOR with single byte keys
print("\n\nTrying single-byte XOR keys:")
for key in range(256):
    decrypted = bytes([b ^ key for b in encrypted_data])
    # Check if it contains printable ASCII
    if b'flag' in decrypted.lower() or b'bsides' in decrypted.lower():
        print(f"\nKey 0x{key:02x}: {decrypted}")
    # Check for readable text
    if all(32 <= b < 127 or b in [10, 13] for b in decrypted[:20]):
        print(f"\nKey 0x{key:02x} (readable): {decrypted[:50]}")

# Try XOR with "GT1338" or similar patterns
patterns = [b'GT1338', b'GT13', b'GRAN', b'TURISMO']
for pattern in patterns:
    print(f"\n\nTrying XOR with pattern: {pattern}")
    decrypted = bytearray()
    for i, b in enumerate(encrypted_data):
        decrypted.append(b ^ pattern[i % len(pattern)])
    print(decrypted[:100])
    if b'flag' in decrypted.lower() or b'bsides' in decrypted.lower():
        print(f"FOUND SOMETHING: {decrypted}")
