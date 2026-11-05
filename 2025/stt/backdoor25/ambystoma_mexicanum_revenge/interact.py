#!/usr/bin/env python3
from pwn import *

io = remote('remote.infoseciitr.in', 4005)
io.interactive()
