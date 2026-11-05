#!/usr/bin/env python3

KEYS = ['key0']

try:
    for i in range(4):
        key = KEYS[i]
        print(f"Got key[{i}]: {key}")
except IndexError as e:
    print(f"IndexError: {e}")
except Exception as e:
    print(f"Exception: {e}")
