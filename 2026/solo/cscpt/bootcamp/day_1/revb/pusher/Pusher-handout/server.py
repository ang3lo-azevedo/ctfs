#!/usr/bin/env python3
"""
Server TCP simplu: expune binarul challenge peste retea, ca sa te poti conecta cu

    nc HOST PORT

si sa interactionezi exact ca si cum ai rula binarul local. Flag-ul e citit de
binar din ./flag.txt (langa binar). Fara dependinte externe.

Config prin variabile de mediu:
    HOST     (default 0.0.0.0)
    PORT     (default 1337)
    BIN      (default: ./challenge de langa acest script)
    TLIMIT   (deadline wall-clock per conexiune, secunde, default 120)
    MAXCONN  (conexiuni concurente maxime, default 64)

Rulare:  python3 server.py
"""
import os
import socket
import subprocess
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "1337"))
BIN = os.environ.get("BIN", os.path.join(HERE, "challenge"))
TLIMIT = int(os.environ.get("TLIMIT", "120"))
MAXCONN = int(os.environ.get("MAXCONN", "64"))

_slots = threading.BoundedSemaphore(MAXCONN)


def handle(conn, addr):
    # ruleaza binarul cu cwd = directorul lui, ca sa gaseasca ./flag.txt
    workdir = os.path.dirname(os.path.abspath(BIN))
    try:
        p = subprocess.Popen([BIN], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, cwd=workdir, bufsize=0)
    except OSError as e:
        try:
            conn.sendall(("server error: %s\n" % e).encode())
        finally:
            conn.close()
            _slots.release()
        return

    # Doua fire separate: unul client->binar, altul binar->client. Firele separate
    # evita deadlock-ul de pipe cand ambele directii au date simultan.
    def reader():                                  # client -> stdin binar
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break                          # clientul a inchis scrierea
                p.stdin.write(data)
                p.stdin.flush()
        except (OSError, ValueError):
            pass
        finally:
            try:
                p.stdin.close()                    # EOF catre binar
            except OSError:
                pass

    def writer():                                  # stdout binar -> client
        pout = p.stdout.fileno()
        try:
            while True:
                data = os.read(pout, 4096)
                if not data:
                    break                          # binarul a iesit -> gata
                conn.sendall(data)
        except (OSError, ValueError):
            pass

    rt = threading.Thread(target=reader, daemon=True)
    wt = threading.Thread(target=writer, daemon=True)
    rt.start()
    wt.start()

    # deadline wall-clock pe intreaga conexiune (nu se re-armeaza pe activitate)
    wt.join(timeout=TLIMIT)
    try:
        p.kill()                                   # opreste binarul (deadline sau EOF)
    except OSError:
        pass
    try:
        conn.close()                               # deblocheaza reader-ul blocat in recv
    except OSError:
        pass
    try:
        p.wait(timeout=5)                          # reap, fara zombie
    except Exception:
        pass
    _slots.release()


def main():
    if not os.path.exists(BIN):
        sys.exit("[!] binar inexistent: %s (seteaza BIN=... sau compileaza-l)" % BIN)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(MAXCONN)
    print("[*] serving %s on %s:%d (max %d conns, %ds/conn)"
          % (BIN, HOST, PORT, MAXCONN, TLIMIT), file=sys.stderr)
    while True:
        conn, addr = s.accept()
        _slots.acquire()                           # capac concurenta
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
