import os


def get_config_value(key):
    value = os.environ.get(key)
    assert value, f"Please, set up the {key} env variable"
    return value


DATA_PATH = get_config_value('DATA_PATH')
CACHE_PATH = os.path.join(DATA_PATH, 'cache')
