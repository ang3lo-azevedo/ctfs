import pydantic
import os

def my_func():
    print("my_func called!")
    return str

try:
    Blueprint = create_model("Test", foo="my_func()")
    print(Blueprint.model_json_schema())
    b = Blueprint.model_validate_json('{"foo": "hi"}', strict=True)
    print(b)
except Exception as e:
    print(e)
