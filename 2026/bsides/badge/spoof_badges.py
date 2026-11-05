#!/usr/bin/env python3
"""Spoof N fake 'BSL-xxxxxx' BLE badges by rotating identities on an adapter.

The BSides badge recognises peers by the BLE Complete Local Name 'BSL-xxxxxx'
(no manufacturer/service data). One radio can only advertise one identity at a
time, so we cycle through N fake identities fast enough that a scanner sees them
all within its scan window.

Run as root:   sudo python3 spoof_badges.py [N] [hold_seconds] [hciX]
Ctrl+C to stop (it disables advertising on exit).
"""
import subprocess, struct, time, random, string, sys, atexit

N      = int(sys.argv[1]) if len(sys.argv) > 1 else 5
HOLD   = float(sys.argv[2]) if len(sys.argv) > 2 else 0.6     # seconds each identity is on air
DEV    = sys.argv[3] if len(sys.argv) > 3 else "hci0"

def hci(ogf, ocf, data=b""):
    # hcitool -i hciX cmd <ogf> <ocf> <bytes...>
    args = ["hcitool", "-i", DEV, "cmd", f"0x{ogf:02x}", f"0x{ocf:04x}"]
    args += [f"{b:02x}" for b in data]
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)

def adv_enable(on):      hci(0x08, 0x000a, bytes([1 if on else 0]))
def set_random(addr6):   hci(0x08, 0x0005, addr6[::-1])          # addr is LSB-first on the wire
def set_params():
    # interval 100ms, ADV_NONCONN_IND(0x03), own addr = random(0x01), all channels(0x07)
    p = struct.pack("<HHBBB6sBB", 0x00A0, 0x00A0, 0x03, 0x01, 0x00, b"\x00"*6, 0x07, 0x00)
    hci(0x08, 0x0006, p)
def set_adv_data(name):
    nm = name.encode()
    ad = bytes([0x02,0x01,0x06]) + bytes([len(nm)+1, 0x09]) + nm   # Flags + Complete Local Name
    ad = ad[:31]
    hci(0x08, 0x0008, bytes([len(ad)]) + ad + b"\x00"*(31-len(ad)))

def rand_name():
    return "BSL-" + "".join(random.choices(string.ascii_letters+string.digits, k=6))
def rand_addr():
    a = bytearray(random.getrandbits(8) for _ in range(6))
    a[5] |= 0xC0                      # top two bits = 1 -> valid "static random" address
    return bytes(a)

ids = [(rand_name(), rand_addr()) for _ in range(N)]
print(f"[*] spoofing {N} fake badges on {DEV}, {HOLD}s each:")
for nm, ad in ids:
    print(f"      {nm}  {':'.join(f'{b:02x}' for b in ad[::-1])}")

atexit.register(lambda: (adv_enable(False)))
print("[*] broadcasting... Ctrl+C to stop")
try:
    while True:
        for nm, ad in ids:
            adv_enable(False)
            set_random(ad)
            set_params()
            set_adv_data(nm)
            adv_enable(True)
            time.sleep(HOLD)
except KeyboardInterrupt:
    print("\n[*] stopping, advertising disabled.")
