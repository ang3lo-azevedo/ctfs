from pydantic import create_model
import os
os.environ['FLAG'] = 'GPNCTF{test_flag}'

try:
    Blueprint = create_model("Test", foo="__import__('os').environ['FLAG']")
    print(Blueprint.model_json_schema())
except Exception as e:
    import traceback
    traceback.print_exc()
