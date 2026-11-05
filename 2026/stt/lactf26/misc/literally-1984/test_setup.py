#!/usr/bin/env python3
import sys

def test_setup():
    evts = 0
    def g(evt, *args):
        nonlocal evts
        evts += 1
        print(f"Event {evts}: {evt}")
        if evts > 3:
            print("literally 1984")
            import os
            os._exit(1)
    
    sys.addaudithook(g)
    print(f"\n=== After hook setup, events so far: {evts} ===\n")
    
    # Now run our payload
    print("Running: eval(\"print([*open(chr(102)+chr(108)+chr(97)+chr(103))])\")")
    eval("print([*open(chr(102)+chr(108)+chr(97)+chr(103))])")
    print(f"\n=== Total events: {evts} ===")

test_setup()
