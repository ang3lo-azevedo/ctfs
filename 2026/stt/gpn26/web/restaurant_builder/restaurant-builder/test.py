from pydantic import create_model
try:
    Blueprint = create_model("Test", foo="bar")
    print(Blueprint.model_json_schema())
except Exception as e:
    print(e)
