#!/usr/bin/env python3
# Analyzing audit events

import sys

count = 0
def audit_hook(event, args):
    global count
    count += 1
    print(f"Event {count}: {event} - {args}")

sys.addaudithook(audit_hook)

# Test what triggers audit events
print("\n=== Testing: open(chr(102)+chr(108)+chr(97)+chr(103)).read() ===")
try:
    result = eval("open(chr(102)+chr(108)+chr(97)+chr(103)).read()")
    print(f"Result: {result}")
except:
    pass

print(f"\nTotal events: {count}")
