import functools
import hashlib
import json
import os
import re

from llm_function.common import config


def make_path_safe(s):
    pattern = r'[^a-zA-Z0-9_\-\.]'
    safe_string = re.sub(pattern, '_', s)

    return safe_string


def get_cache_key_based_on_all_args(*args, **kwargs):
    """Serialize and hash arguments and keyword arguments."""
    serialized = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def ensure_dir_exists(path):
    """Ensure that a given directory exists."""
    if not os.path.exists(path):
        os.makedirs(path)


def cached(func_name: str, gen_cache_filename=get_cache_key_based_on_all_args):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_dir = os.path.join(config.CACHE_PATH, func_name)
            ensure_dir_exists(cache_dir)

            cache_filename = gen_cache_filename(*args, **kwargs)
            cache_filename = make_path_safe(cache_filename)
            cache_path = os.path.join(cache_dir, cache_filename)

            # If result exists in cache, read and return it
            if os.path.exists(cache_path):
                with open(cache_path) as f:
                    return json.load(f)

            # If result not in cache, call the original function
            result = await func(*args, **kwargs)

            # Save the result to cache
            with open(cache_path, 'w') as f:
                json.dump(result, f)

            return result

        return wrapper

    return decorator
