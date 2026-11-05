import socket
import time

# Server connection details
server_host = "foren-1f49f8dc.p1.securinets.tn"
server_port = 1337

# Forensics investigation results
forensics_data = [
    "122b2b4bf1433341ba6e8fefd707379a98e6e9ca376340379ea42edb31a5dba2",
    "19045",
    "192.168.206.131",
    "thunderbird",
    "ammar55221133@gmail.com",
    "masmoudim522@gmail.com",
    "https://tmpfiles.org/dl/23860773/sys.exe",
    "be4f01b3d537b17c5ba7dc1bb7cd4078251364398565a0ca1e96982cff820b6d",
    "40.113.161.85",
    "5000",
    "http://40.113.161.85:5000/helppppiscofebabe23",
    "3649ba90-266f-48e1-960c-b908e1f28aef",
    "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run\MyApp",
    "C:\Users\\ammar\Documents\sys.exe",
    "e7bcc0ba5fb1dc9cc09460baaa2a6986"

]

try:
    print(f"[+] Connecting to {server_host}:{server_port}")
    
    # Create socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((server_host, server_port))
    
    print("[+] Connected successfully!")
    
    # Receive initial message from server
    initial_response = sock.recv(4096).decode('utf-8', errors='ignore')
    print(f"[*] Server initial message:\n{initial_response}")
    
    # Send each piece of data line by line with delay
    for i, data in enumerate(forensics_data, 1):
        print(f"\n[{i:2d}/11] Sending: {data}")
        
        # Send the data
        sock.send((data + '\n').encode('utf-8'))
        
        # Wait for server response
        time.sleep(0.5)  # Small delay between sends
        try:
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            if response.strip():
                print(f"[*] Server response: {response.strip()}")
        except socket.timeout:
            print("[*] No immediate response from server")
        
except ConnectionRefusedError:
    print("[-] Error: Connection refused. Server might be down.")
except socket.timeout:
    print("[-] Error: Connection timeout")
except Exception as e:
    print(f"[-] Error: {e}")
finally:
    try:
        sock.close()
        print("[+] Connection closed")
    except:
        pass
    