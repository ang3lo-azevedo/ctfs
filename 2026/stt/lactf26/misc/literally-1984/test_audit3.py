#!/usr/bin/env python3
import sys

# Test different ways to read a file with minimal audit events
count = 0
def audit_hook(event, args):
    global count
    count += 1
    print(f"Event {count}: {event}")

sys.addaudithook(audit_hook)

# Test 1: List unpacking
print("\n=== Test: [*open(chr(102)+chr(108)+chr(97)+chr(103))] ===")
count = 0
try:
    result = eval("print([*open(chr(102)+chr(108)+chr(97)+chr(103))])")
except Exception as e:
    print(f"Error: {e}")
print(f"Total: {count} events\n")

# Test 2: next()
print("=== Test: next(open(chr(102)+chr(108)+chr(97)+chr(103))) ===")
count = 0
try:
    result = eval("print(next(open(chr(102)+chr(108)+chr(97)+chr(103))))")
except Exception as e:
    print(f"Error: {e}")
print(f"Total: {count} events\n")

# Test 3: Just open (no read)
print("=== Test: open(chr(102)+chr(108)+chr(97)+chr(103)) ===")
count = 0
try:
    result = eval("print(open(chr(102)+chr(108)+chr(97)+chr(103)))")
except Exception as e:
    print(f"Error: {e}")
print(f"Total: {count} events\n")
