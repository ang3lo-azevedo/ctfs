#!/usr/bin/env python3
import re
import socket

from Crypto.Hash import TupleHash128


HOST = "challenges.cybersecuritychallenge.pt"
PORT = 24302

GENERATOR = 0x2
Q = 4863582031353698198761328444493879228310321364281230162432941418974766035646994473626431630074195869892666977725902703437672528883791089201079706878830495677314851995801210780927161054477270449206302430992983000362680537603073911181954436112981857313308698944840733489877808410943336233052503234913545497471564833465501423042038660248491510385678358194559059271654320944019327351043166386768574242028957654775069955451796948455362239879097118518200743383781792266381988326107437550218806712025903303696479597447784386404544762534889281069284960359265592322943158476484143869956733696787606184300373875007099479039839737235636800602135437322790489431635178114950297146384525504411311985677915624022281816199470525512536884444099066124586374766347855189025988552225935417330198821849818515883717265006356649038533599313538003254211409511373248001631185015759679768429197412497657484402329229273463264931927078841128724273334163


def recv_until(sock: socket.socket, needle: bytes, limit: int = 1_000_000) -> bytes:
    data = b""
    while needle not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(data) > limit:
            raise RuntimeError("recv limit exceeded")
    return data


def compute_c(h: int) -> int:
    th = TupleHash128.new(digest_bytes=400)
    th.update(GENERATOR.to_bytes(400, "big"))
    th.update(Q.to_bytes(400, "big"))
    th.update(h.to_bytes(400, "big"))
    return int.from_bytes(th.digest(), "big")


def parse_h(banner: str) -> int:
    m = re.search(r"public key:\s*([0-9\s]+)\n", banner)
    if not m:
        raise ValueError("Could not find public key in banner")
    digits = re.sub(r"\s+", "", m.group(1))
    return int(digits)


def forge_proof(h: int):
    # Vulnerability: the challenge c is constant and does not depend on u.
    # Choose any z, then set u = g^z * (h^c)^-1 (mod Q).
    c = compute_c(h)
    z = 1
    inv = pow(pow(h, c, Q), -1, Q)
    u = (pow(GENERATOR, z, Q) * inv) % Q
    return u, c, z


def main():
    with socket.create_connection((HOST, PORT), timeout=10) as s:
        s.settimeout(10)
        data = recv_until(s, b"choice:")
        banner = data.decode("utf-8", "ignore")
        h = parse_h(banner)

        u, c, z = forge_proof(h)

        s.sendall(b"1\n")
        recv_until(s, b"u:")
        s.sendall(f"{u}\n".encode())
        recv_until(s, b"c:")
        s.sendall(f"{c}\n".encode())
        recv_until(s, b"z:")
        s.sendall(f"{z}\n".encode())

        chunks: list[bytes] = []
        while True:
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            chunks.append(chunk)

        print(b"".join(chunks).decode("utf-8", "ignore"))


if __name__ == "__main__":
    main()
