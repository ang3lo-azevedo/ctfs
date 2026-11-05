#!/usr/bin/env python3
import requests
import os

URL = "http://localhost:6969/interpol8"

# Key insight: we can overwrite json_handler!
# We need json_handler.dumps to somehow return the FLAG

# In Python, os.environ is a dict-like object
# os.environ['FLAG'] would give us the flag
# But we need something where calling .dumps() gives us access

# What if we make json_handler be os.environ?
# Then json_handler.dumps would fail, but maybe we can use a different return type?

# Or better yet: what if we make json_handler.dumps be os.getenv?
# Then when it calls json_handler.dumps(self.__get_dict__()), it would call os.getenv(dict)
# That won't work...

# Wait, let me think about the XML handler
# Line 55: return self.xml_handler.unparse(self.__get_dict__())
# xmltodict.unparse() expects a dict and returns a string

# What if we overwrite xml_handler with os?
# Then xml_handler.environ would give us the environment!
# But we need to access it...

# Actually, let's look at __getitem__ on line 25:
# def __getitem__(self, key):
#     return pydash.get(self, key)

# This means if we set {"FLAG": "value"}, we can access it via holder["FLAG"]!
# But how do we get the FLAG into the holder?

# The real trick: we need to inject the FLAG value into the response!
# If we make the holder contain {"FLAG": actual_flag_value}

# Can we inject through merge? Line 46: self._setitems(other.__get_dict__())
# This means holder2's dict gets merged into holder1

# What if holder2 contains the FLAG from environment?
# We need to read os.environ['FLAG'] somehow...

print("=== Test: Can we use os.environ? ===")
# The issue is we can't execute code, we can only set attributes

# Wait! Looking at line 18-19:
# if type(v) == list:
#     v = tuple(v)
# Lists become tuples!

# And line 21-22:
# if type(v) == dict:
#     self._setitems(v, path + [k])
# Dicts are recursively processed!

# So the structure of data directly becomes attributes on the object
# We control the structure, and it becomes the object's attributes

# What if we make json_handler be a dict that has a 'dumps' key?
# And that 'dumps' key points to something that reveals the flag?

payload = {
    "doc1": '{"json_handler": {"dumps": "os.environ"}}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")

# Let me try a different approach
# What if we directly put FLAG in the holder?
print("=== Test 2: Direct FLAG injection (wishful thinking) ===")
payload = {
    "doc1": '{"FLAG": "test"}',
    "doc2": '{"dummy": "data"}',
    "type1": "json",
    "type2": "json",
    "return_type": "json"
}

response = requests.post(URL, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}\n")
