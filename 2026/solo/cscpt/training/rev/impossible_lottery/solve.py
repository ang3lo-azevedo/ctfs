#!/usr/bin/env python3

import argparse
import re
import socket


def recv_until_prompt(sock: socket.socket) -> str:
    data = b""
    while b"original secret" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data.decode("utf-8", "ignore")


def parse_challenge(text: str) -> tuple[int, list[int]]:
    lucky_match = re.search(r"lucky number is\s+(\d+)", text, re.IGNORECASE)
    if lucky_match is None:
        raise ValueError("Could not parse lucky number")
    lucky = int(lucky_match.group(1))

    draws = re.findall(r"Draw number\s+\d+\s*:\s*(\d+)", text, re.IGNORECASE)
    if len(draws) != 8:
        raise ValueError(f"Expected 8 draws, got {len(draws)}")

    return lucky, [int(value) for value in draws]


def recover_secret_bytes(generator_outputs: list[int]) -> bytes:
    bit_matrix = [[0] * 8 for _ in range(8)]

    for round_index, value in enumerate(generator_outputs):
        for rotated_index in range(8):
            bit = (value >> (7 - rotated_index)) & 1
            byte_index = (rotated_index + round_index) % 8
            bit_matrix[byte_index][round_index] = bit

    secret = bytes(
        sum(bit_matrix[byte_index][bit_index] << bit_index for bit_index in range(8))
        for byte_index in range(8)
    )
    return secret


def solve(host: str, port: int) -> str:
    with socket.create_connection((host, port), timeout=8) as sock:
        banner = recv_until_prompt(sock)
        lucky, masked_draws = parse_challenge(banner)

        generator_outputs = [draw ^ lucky for draw in masked_draws]
        secret = recover_secret_bytes(generator_outputs)

        sock.sendall(secret.hex().encode() + b"\n")

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

    return banner + response.decode("utf-8", "ignore")


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve impossible_lottery challenge")
    parser.add_argument("--host", default="challenges.cybersecuritychallenge.pt")
    parser.add_argument("--port", type=int, default=23521)
    args = parser.parse_args()

    result = solve(args.host, args.port)
    print(result)


if __name__ == "__main__":
    main()
