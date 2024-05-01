import json


def spread(obj, keys):
    return (obj.get(key) for key in keys)


def deep(obj: dict, path: str):
    keys = path.split('.')
    res = obj
    for key in keys:
        res = res.get(key)
        if not res:
            break
    return res


def exclude(obj, keys):
    return {k: v for k, v in obj.items() if k not in keys}


def json_print(obj: dict):
    print(json.dumps(obj, indent=2, ensure_ascii=False))
