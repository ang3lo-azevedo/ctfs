from fastapi import FastAPI, Body, HTTPException
from pydantic import create_model
from typing import Dict

app = FastAPI()
blueprints = {}
items = {}

@app.get("/")
def home():
    return "The department of restaurant safety inspections thanks you for your cooperation."

@app.get("/blueprint/{name}")
def get_blueprint(name: str):
    blueprint = blueprints.get(name)
    if blueprint is None:
        return None
    return blueprint.model_json_schema()

@app.post("/blueprint/{name}")
def register_blueprint(name: str, description: Dict[str,str] = Body()):
    if name in blueprints:
        raise HTTPException(status_code=409, detail="We already know that one. But keep looking, I think there are some spoons missing.")

    description = {k: v for k,v in description.items() if not k.startswith("__")}
    Blueprint = create_model(name, **description)
    blueprints[name] = Blueprint

    return "Blueprint successfully registered"

@app.get("/item/{name}")
def get_item(name: str):
    return items.get(name)

@app.post("/item/{name}")
def register_item(name: str, item: str = Body()):
    if name not in blueprints:
        raise HTTPException(status_code=400, detail="That looks interesting but we don't know what it is. Are you sure it belongs in a kitchen?")
    try:
        items[name] = blueprints[name].model_validate_json(item, strict=True)
    except:
        raise HTTPException(status_code=409, detail="Are you sure you followed the blueprint exactly?")
    return "Item successfully registered"
