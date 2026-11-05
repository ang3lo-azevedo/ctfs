import re
import socket

HOST = "challenges.cybersecuritychallenge.pt"
PORT = 24301


def recv_until(sock, marker: bytes) -> bytes:
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    return data


def sendline(sock, text: str) -> None:
    sock.sendall(text.encode() + b"\n")


def parse_wallet_and_sig(blob: bytes):
    text = blob.decode(errors="ignore")
    wallet_match = re.search(r"Here is your wallet: (\{.*?\})", text)
    sig_match = re.search(r"Here is the signature: ([A-Za-z0-9+/=]+)", text)
    if not wallet_match or not sig_match:
        return None, None
    return wallet_match.group(1), sig_match.group(1)


def main():
    sock = socket.create_connection((HOST, PORT), timeout=10)

    recv_until(sock, b"name?\n")
    sendline(sock, "alice")

    intro = recv_until(sock, b">>> ")
    base_wallet, base_sig = parse_wallet_and_sig(intro)
    if not base_wallet:
        raise RuntimeError("Could not parse initial wallet/signature")

    rich_wallet = None
    rich_sig = None

    for _ in range(40):
        sendline(sock, "1")
        recv_until(sock, b">>> ")
        sendline(sock, base_wallet)
        recv_until(sock, b">>> ")
        sendline(sock, base_sig)
        recv_until(sock, b">>> ")
        sendline(sock, "-2000000000")

        round_out = recv_until(sock, b">>> ")
        text = round_out.decode(errors="ignore")

        if "You lost" in text:
            rich_wallet, rich_sig = parse_wallet_and_sig(round_out)
            break

    if not rich_wallet:
        raise RuntimeError("Did not hit a losing round in time")

    sendline(sock, "2")
    recv_until(sock, b">>> ")
    sendline(sock, rich_wallet)
    recv_until(sock, b">>> ")
    sendline(sock, rich_sig)

    final = sock.recv(8192).decode(errors="ignore")
    print(final)
    sock.close()


if __name__ == "__main__":
    main()
