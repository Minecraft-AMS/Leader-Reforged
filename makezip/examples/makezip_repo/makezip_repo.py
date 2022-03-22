from makezip import MakeZip

def construct(path: str = "./makezip/__init__.py"):
    with open(path, "r+") as file:
        content = file.readline().rstrip()[3:-3]
    return {
        "$VERSION$": content[content.find("v"):]
    }

MakeZip(CONSTRUCTOR_FUNCTION = construct).make()