#!/usr/bin/env python3

import hashlib
import hmac
import os
import socketserver
from typing import Optional, Tuple
import secrets

p = 170141183460469231731687303715884105727
a = p - 3
b = 12345678901234567890123456789012345678

secret = secrets.randbelow(p - 1) + 1
secret_bits = len(bin(secret)) - 2

msg = b"Cristiano Ronaldo is the GOAT"

FLAG = os.environ.get("FLAG", "CSCPT{test_flag}").encode()

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


def encrypt_flag(secret: int) -> str:
    key = hashlib.sha256(str(secret).encode()).digest()
    stream = keystream(key, len(FLAG))
    return xor_bytes(FLAG, stream).hex()


class ChallengeHandler(socketserver.StreamRequestHandler):
    def send_line(self, data: str) -> None:
        self.wfile.write(data.encode() + b"\n")
        self.wfile.flush()

    def prompt(self) -> None:
        self.wfile.write(b"> ")
        self.wfile.flush()

    def handle(self) -> None:
        self.send_line("Welcome to our new cryptographic system. Enjoy the final days of the offer, as it will be launched commercially very soon.")
        self.send_line("")
        self.send_line(f"p = {p}")
        self.send_line(f"a = {a}")
        self.send_line(f"b = {b}")
        self.send_line(f"secret_bits = {secret_bits}")
        self.send_line("")
        self.send_line("Commandos:")
        self.send_line("  GET x y   - multiply your point by the server secret and return a MAC")
        self.send_line("  FLAG      - return encrypted flag")
        self.send_line("  QUIT      - close connection")
        self.send_line("")
        self.prompt()

        while True:
            line = self.rfile.readline()
            if not line:
                return

            line = line.decode(errors="replace").strip()
            if not line:
                self.prompt()
                continue

            parts = line.split()
            command = parts[0].upper()

            try:
                if command == "QUIT":
                    self.send_line("bye")
                    return

                if command == "FLAG":
                    self.send_line(f"ct={encrypt_flag(secret)}")
                    self.prompt()
                    continue

                if command == "GET":
                    if len(parts) != 3:
                        self.send_line("error=usage: GET x y")
                        self.prompt()
                        continue

                    x = int(parts[1], 0) % p
                    y = int(parts[2], 0) % p

                    attacker_point = (x, y)

                    shared_point = ec_mul(secret, attacker_point)
                    mac = oracle_mac(shared_point)

                    self.send_line(f"mac={mac}")
                    self.prompt()
                    continue

                self.send_line("error=unknown command")
                self.prompt()

            except Exception as exc:
                self.send_line(f"error={type(exc).__name__}: {exc}")
                self.prompt()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "1337"))

    with ThreadedTCPServer((host, port), ChallengeHandler) as server:
        print(f"Listening on {host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    main()
