import webcolors


example = {"key": "vallue"}

def check(data) -> bool:
    data.update({"value": "key"})
    return False


check(example)

print(

