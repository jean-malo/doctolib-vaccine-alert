import os
from typing import Any


def read_config_value(config, section, key, var_type: Any = str, fallback=None):
    env_var_key = f"{section.upper()}__{key.upper()}"
    env_value = os.getenv(env_var_key)
    if env_value:
        if var_type == bool:
            return env_value.lower() in ('true', '1', 't')
        return var_type(env_value)
    else:
        fallback = var_type(fallback)
    if var_type == str:
        return config.get(section, key, fallback=fallback)
    elif var_type == int:
        return config.getint(section, key, fallback=fallback)
    elif var_type == float:
        return config.getfloat(section, key, fallback=fallback)
    elif var_type == bool:
        return config.getboolean(section, key, fallback=fallback)


def to_list(string_separated):
    if not string_separated:
        return []
    return string_separated.split(",")
