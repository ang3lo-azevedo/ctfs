#!/usr/bin/env python3
import sys

count = 0
def audit_hook(event, args):
    global count
    count += 1
    print(f"Event {count}: {event}")

sys.addaudithook(audit_hook)

# Simulate what the challenge does
print("=== Running: eval(\"print(open(chr(102)+chr(108)+chr(97)+chr(103)).read())\") ===")
count = 0
try:
    eval("print(open(chr(102)+chr(108)+chr(97)+chr(103)).read())")
except Exception as e:
    print(f"Error: {e}")
print(f"Total: {count} events")

print("\n=== Running: eval(\"print([*open(chr(102)+chr(108)+chr(97)+chr(103))])\") ===")
count = 0
try:
    eval("print([*open(chr(102)+chr(108)+chr(97)+chr(103))])")
except Exception as e:
    print(f"Error: {e}")
print(f"Total: {count} events")
