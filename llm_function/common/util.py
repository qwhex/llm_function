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


def extract_json(message):
    start_index = message.find('{')
    end_index = message.rfind('}')

    if start_index != -1 and end_index != -1:
        json_part = message[start_index:end_index + 1]
        try:
            json_data = json.loads(json_part)
            return json_data
        except json.JSONDecodeError:
            raise ValueError('Invalid JSON')
    else:
        raise ValueError('No JSON found in message')
