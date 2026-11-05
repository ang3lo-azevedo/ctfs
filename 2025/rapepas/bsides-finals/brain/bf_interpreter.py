#!/usr/bin/env python3
"""Simple Brainfuck interpreter"""
import sys

def brainfuck(code):
    tape = {}  # Use dictionary for sparse array
    ptr = 0
    code_ptr = 0
    output = []
    
    # Build jump table for brackets
    jumps = {}
    stack = []
    for i, cmd in enumerate(code):
        if cmd == '[':
            stack.append(i)
        elif cmd == ']':
            if stack:
                start = stack.pop()
                jumps[start] = i
                jumps[i] = start
    
    while code_ptr < len(code):
        cmd = code[code_ptr]
        
        if cmd == '>':
            ptr += 1
        elif cmd == '<':
            ptr -= 1
        elif cmd == '+':
            if ptr not in tape:
                tape[ptr] = 0
            tape[ptr] = (tape[ptr] + 1) % 256
        elif cmd == '-':
            if ptr not in tape:
                tape[ptr] = 0
            tape[ptr] = (tape[ptr] - 1) % 256
        elif cmd == '.':
            val = tape.get(ptr, 0)
            output.append(chr(val))
            print(chr(val), end='', flush=True)
        elif cmd == ',':
            tape[ptr] = ord(sys.stdin.read(1))
        elif cmd == '[':
            if tape.get(ptr, 0) == 0:
                code_ptr = jumps[code_ptr]
        elif cmd == ']':
            if tape.get(ptr, 0) != 0:
                code_ptr = jumps[code_ptr]
        
        code_ptr += 1
    
    return ''.join(output)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 bf_interpreter.py <brainfuck_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        code = f.read()
    
    brainfuck(code)
