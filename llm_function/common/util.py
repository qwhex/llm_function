import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


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


def escape_control_characters(content: str) -> str:
    """
    Escapes control characters in a JSON string by replacing them with their Unicode equivalents.

    Args:
        content (str): The JSON string to process.

    Returns:
        str: The processed JSON string with control characters escaped.
    """

    def escape_string(match) -> str:
        s = match.group(0)
        s = s[1:-1]  # Remove the surrounding quotes
        # Replace specific escaped control characters with Unicode
        s = s.replace("\\n", "\\u000a")
        s = s.replace("\\t", "\\u0009")
        s = s.replace("\\r", "\\u000d")
        s = s.replace("\\b", "\\u0008")
        s = s.replace("\\f", "\\u000c")
        s = s.replace("\\a", "\\u0007")
        s = s.replace("\\x00", "\\u0000")
        # Replace any remaining raw control characters
        s = re.sub(r"[\x00-\x1f\x7f-\x9f]", lambda m: "\\u%04x" % ord(m.group(0)), s)
        return f'"{s}"'

    pattern = re.compile(r'"(?:[^"\\]|\\.)*"')

    return pattern.sub(escape_string, content)


def extract_json_object(message: str) -> dict[str, Any]:
    """
    Extracts the largest valid JSON object from a message string.
        Note: max nesting depth is 4.

    Args:
        message (str): The message containing JSON objects.

    Returns:
        Dict[str, Any]: The extracted JSON object.

    Raises:
        ValueError: If no valid JSON object is found.
    """
    # Use regex to find potential JSON objects
    json_pattern = r"\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})*\}"
    json_candidates = re.findall(json_pattern, message)

    if not json_candidates:
        raise ValueError("No JSON object found in string")

    # Sort candidates by length in descending order
    json_candidates.sort(key=len, reverse=True)

    # Attempt to parse each JSON candidate
    for json_candidate in json_candidates:
        try:
            json_data: Dict[str, Any] = json.loads(json_candidate)
            return json_data
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Invalid JSON: {message[:65]}...")

