import json
from makezip import MakeZip


def construct(path: str = "./mcdreforged.plugin.json"):
    with open(path, "r+") as file:
        content = json.load(file)
    plugin_id = content["id"]
    version = content["version"]
    return {"$PLUGIN_ID$": plugin_id, "$VERSION$": version}


MakeZip(CONSTRUCTOR_FUNCTION=construct).make()
