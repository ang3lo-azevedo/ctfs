#!/usr/bin/env python3

forbidden = " _.\\\"'{}#="
payloads = [
    "open(chr(102)+chr(108)+chr(97)+chr(103)).read()",
    "[*open(chr(102)+chr(108)+chr(97)+chr(103))]",
]

for p in payloads:
    has_bad = any(c in forbidden for c in p)
    bad_chars = [c for c in p if c in forbidden]
    print(f"{p}")
    print(f"  Length: {len(p)}, Has forbidden: {has_bad}, Bad chars: {bad_chars}")
    print()
