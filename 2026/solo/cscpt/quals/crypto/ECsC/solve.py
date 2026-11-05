#!/usr/bin/env python3

import hashlib
import hmac
import socket
import time
from typing import Optional, Tuple

p = 170141183460469231731687303715884105727
a = p - 3
b_singular = 2
msg = b"Cristiano Ronaldo is the GOAT"

Point = Optional[Tuple[int, int]]


def inv_mod(x: int) -> int:
    x %= p
    if x == 0:
        raise ZeroDivisionError("inverse of zero")
    return pow(x, -1, p)


def ec_add(p1: Point, p2: Point) -> Point:
    if p1 is None:
        return p2
    if p2 is None:
        return p1

    x1, y1 = p1
    x2, y2 = p2

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if p1 == p2:
        if y1 % p == 0:
            return None
        slope = ((3 * x1 * x1 + a) * inv_mod(2 * y1)) % p
    else:
        slope = ((y2 - y1) * inv_mod(x2 - x1)) % p

    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p

    return x3, y3


def ec_mul(k: int, point: Point) -> Point:
    result: Point = None
    addend = point

    while k > 0:
        if k & 1:
            result = ec_add(result, addend)
        addend = ec_add(addend, addend)
        k >>= 1

    return result


def point_to_bytes(point: Point) -> bytes:
    if point is None:
        return b"POINT_AT_INFINITY"
    x, y = point
    return f"{x},{y}".encode()


def shared_key_from_point(point: Point) -> bytes:
    return hashlib.sha256(point_to_bytes(point)).digest()


def oracle_mac(point: Point) -> str:
    key = shared_key_from_point(point)
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def keystream(seed: bytes, length: int) -> bytes:
    out = b""
    counter = 0
    while len(out) < length:
        block = hashlib.sha256(seed + counter.to_bytes(8, "big")).digest()
        out += block
        counter += 1
    return out[:length]


def decrypt_flag(secret: int, ct_hex: str) -> bytes:
    key = hashlib.sha256(str(secret).encode()).digest()
    ct = bytes.fromhex(ct_hex)
    stream = keystream(key, len(ct))
    return xor_bytes(ct, stream)


def find_point_on_curve(b_val: int) -> Point:
    """Find a random nonsingular point on y² = x³ + ax + b_val."""
    import random
    while True:
        x = random.randint(0, p - 1)
        if b_val == 2 and x == 1:
            continue
        if b_val == p - 2 and x == p - 1:
            continue
        y_sq = (pow(x, 3, p) + (a * x) % p + b_val) % p
        if pow(y_sq, (p - 1) // 2, p) == 1:
            y = pow(y_sq, (p + 1) // 4, p)
            return (x, y)


def find_generator() -> Point:
    """Find a generator of the nonsingular group of the singular curve (order 2^127)."""
    print("[*] Finding generator on singular curve...")
    while True:
        P = find_point_on_curve(b_singular)
        half_order = 1 << 126
        test = ec_mul(half_order, P)
        if test is not None:
            print(f"[+] Found generator P = ({P[0]}, {P[1]})")
            return P


class ServerConnection:
    """Connection to the challenge server with proper prompt handling."""
    def __init__(self, host: str, port: int):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((host, port))
        self.buffer = b""

    def _recv_until_prompt(self) -> str:
        """Read data until we see the prompt '> ' (without trailing newline).
        Returns everything before the prompt."""
        while True:
            # Check if we already have a complete response in buffer
            # The prompt is '> ' at the end of the stream
            # But there might be '> ' in MAC output, so we need to be careful
            # Actually, responses end with '\n> ' - the prompt follows a newline
            idx = self.buffer.rfind(b"\n> ")
            if idx != -1:
                data = self.buffer[:idx]
                self.buffer = self.buffer[idx + 3:]  # Skip '\n> '
                return data.decode(errors="replace")

            # Read more data
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout:
                # If we have partial data, return what we have
                if self.buffer:
                    data = self.buffer
                    self.buffer = b""
                    return data.decode(errors="replace")
                raise

            if not chunk:
                # Connection closed
                if self.buffer:
                    data = self.buffer
                    self.buffer = b""
                    return data.decode(errors="replace")
                raise ConnectionError("Connection closed by server")

            self.buffer += chunk

    def send_cmd(self, cmd: str) -> str:
        """Send a command and return the response line (before the prompt)."""
        self.sock.sendall((cmd + "\n").encode())
        time.sleep(0.02)  # Small delay to let server process
        response = self._recv_until_prompt()
        return response

    def read_banner(self) -> str:
        """Read the initial banner."""
        banner = self._recv_until_prompt()
        return banner

    def get_mac(self, point: Point) -> str:
        """Send GET command and return the MAC hex string."""
        x, y = point
        response = self.send_cmd(f"GET {x} {y}")
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("mac="):
                return line[4:]
            if line.startswith("error="):
                raise Exception(f"Server error: {line}")
        raise Exception(f"No MAC in response: {response!r}")

    def get_ct(self) -> str:
        """Send FLAG command and return the ciphertext hex string."""
        response = self.send_cmd("FLAG")
        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("ct="):
                return line[3:]
            if line.startswith("error="):
                raise Exception(f"Server error: {line}")
        raise Exception(f"No ct in response: {response!r}")

    def close(self):
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.sock.close()


def recover_secret(host: str, port: int, P: Point) -> int:
    """Recover the secret bit by bit using the singular curve binary search."""
    print(f"[*] Connecting to {host}:{port}...")
    conn = ServerConnection(host, port)

    # Read banner
    banner = conn.read_banner()
    for line in banner.split("\n"):
        if line.strip():
            print(f"    {line.strip()}")

    # Precompute points Q_i = 2^i * P for i = 0..126
    # Q[i] has order 2^(127-i)
    print("[*] Precomputing query points...")
    Q = [None] * 127
    Q[0] = P
    for i in range(1, 127):
        Q[i] = ec_add(Q[i - 1], Q[i - 1])

    secret_mod = 0
    bits_known = 0

    print("[*] Recovering secret bits via binary search...")
    start = time.time()

    for i in range(126, -1, -1):
        mac_target = conn.get_mac(Q[i])

        new_bit = None
        for bit in [0, 1]:
            candidate = secret_mod | (bit << bits_known)
            shared = ec_mul(candidate, Q[i])
            mac_candidate = oracle_mac(shared)
            if mac_candidate == mac_target:
                new_bit = bit
                break

        if new_bit is None:
            print(f"[!] Failed to determine bit {bits_known}")
            print(f"    MAC target: {mac_target}")
            conn.close()
            raise Exception("Bit recovery failed")

        secret_mod = secret_mod | (new_bit << bits_known)
        bits_known += 1

        if bits_known % 16 == 0 or bits_known == 127:
            elapsed = time.time() - start
            print(f"    [{bits_known}/127] recovered ({elapsed:.1f}s)")

    elapsed = time.time() - start
    print(f"[+] Recovery complete in {elapsed:.1f}s")
    conn.close()
    return secret_mod


def get_flag(host: str, port: int) -> str:
    """Connect and get the encrypted flag."""
    print("[*] Fetching encrypted flag...")
    conn = ServerConnection(host, port)
    conn.read_banner()
    ct_hex = conn.get_ct()
    conn.close()
    print(f"[*] ct = {ct_hex}")
    return ct_hex


def main():
    import sys

    host = "challenges.cybersecuritychallenge.pt"
    port = 26302

    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    # Step 1: Find a generator on the singular curve (offline)
    P = find_generator()

    # Step 2: Recover the secret via binary search
    secret = recover_secret(host, port, P)
    print(f"[+] Recovered secret = {secret}")
    print(f"[+] Secret bits = {secret.bit_length()}")

    # Step 3: Get the encrypted flag and decrypt
    ct_hex = get_flag(host, port)
    flag = decrypt_flag(secret, ct_hex)
    print(f"[+] FLAG = {flag.decode()}")

    return 0


if __name__ == "__main__":
    main()
