import json


def _expect_dict(obj: dict) -> None:
    if not isinstance(obj, dict):
        raise TypeError('Expected a dictionary object.')


#
# dict tools:
#

def spread(obj: dict, keys: str | list[str]):
    """
    Extract values from a dictionary based on keys.

    Parameters:
    obj (dict): The dictionary to extract values from.
    keys (str | list[str]): Keys to extract values for.

    Returns:
    list: List of values corresponding to the keys.
    """
    _expect_dict(obj)
    if isinstance(keys, str):
        keys = keys.split(' ')
    return [obj.get(key) for key in keys]


def exclude(obj: dict, keys: str | list[str]):
    """
    Exclude specified keys from a dictionary.

    Parameters:
    obj (dict): The dictionary to exclude keys from.
    keys (str | list[str]): Keys to exclude.

    Returns:
    dict: Dictionary with specified keys excluded.
    """
    _expect_dict(obj)
    if isinstance(keys, str):
        keys = keys.split(' ')
    return {k: v for k, v in obj.items() if k not in keys}


def deep(obj: dict, path: str):
    """
    Retrieve a value deep within a nested dictionary based on a path.

    Parameters:
    obj (dict): The nested dictionary to traverse.
    path (str): Path to the desired value (e.g., 'key1.key2.key3').

    Returns:
    any: The value at the specified path in the dictionary.
    """
    _expect_dict(obj)
    keys = path.split('.')
    res = obj
    for key in keys:
        res = res.get(key)
        if not res:
            return None


#
# json tools:
#

def json_print(obj, indent: int = 2, ensure_ascii: bool = False):
    """
    Pretty-print a JSON object.

    Parameters:
    obj: The JSON object to print.
    indent (int): Number of spaces for indentation (default is 2).
    ensure_ascii (bool): Ensure ASCII characters only (default is False).
    """

    print(json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii))


def extract_json(message: str):
    """
    Extract JSON data from a message string.

    Parameters:
    message (str): The message containing JSON data.

    Returns:
    dict: Extracted JSON data from the message.

    Raises:
    ValueError: If the message does not contain valid JSON.
    """
    start_index = message.find('{')
    end_index = message.rfind('}')

    if start_index != -1 and end_index != -1:
        json_part = message[start_index:end_index + 1]
        try:
            json_data = json.loads(json_part)
            return json_data
        except json.JSONDecodeError:
            summary = message.replace("\n", " ")[:65]
            raise ValueError(f'Invalid JSON: {summary}')
    else:
        raise ValueError('No JSON found in message')
