import pwn
import hashlib

p = pwn.process(["nix-shell", "-p", "nmap", "--run", "ncat --ssl glazed-foie-gras-dusted-with-compressed-hollandaise-eglz.gpn24.ctf.kitctf.de 443"])

p.recvline()

for i in range(100):
    p.recvuntil(b"Commitment (hex): ")
    
    A = b"A"
    B = b"B"
    C = b"C"
    D = f"D{i}".encode()
    
    com_str = A + b"rock" + B + b"paper" + C + b"scissors" + D
    com = hashlib.sha256(com_str).digest().hex()
    
    p.sendline(com.encode())
    
    line = p.recvline().decode().strip()
    bot_choice = line.split()[-1].strip(".")
    
    p.recvuntil(b"What did you choose? ")
    
    if bot_choice == "rock":
        my_choice = "paper"
        r1 = A + b"rock" + B
        r2 = C + b"scissors" + D
    elif bot_choice == "paper":
        my_choice = "scissors"
        r1 = A + b"rock" + B + b"paper" + C
        r2 = D
    elif bot_choice == "scissors":
        my_choice = "rock"
        r1 = A
        r2 = B + b"paper" + C + b"scissors" + D
        
    p.sendline(my_choice.encode())
    
    p.recvuntil(b"Proof (hex): ")
    proof = r1.hex().encode() + b" " + r2.hex().encode()
    p.sendline(proof)

p.interactive()
