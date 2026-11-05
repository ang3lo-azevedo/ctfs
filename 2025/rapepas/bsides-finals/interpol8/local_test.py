#!/usr/bin/env python3

# Local test to understand pydash and attribute manipulation

import pydash

class TestClass:
    class_attr = "class_value"
    
    def __init__(self):
        pass
    
    def method_with_default(self, data, options={}):
        print(f"Options: {options}")
        return data

obj = TestClass()

# Can we set an 'options' attribute and have it affect the method?
pydash.set_(obj, "options", {"interpolate": True})
print(f"obj.options = {obj.options}")

# Call the method
obj.method_with_default("test")

# What if we set options as a nested attribute?
pydash.set_(obj, "method_with_default.options", {"interpolate": True})
print(f"obj.__dict__ = {obj.__dict__}")
