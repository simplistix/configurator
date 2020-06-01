"""
Helpers for specific patterns of usage.
"""

from configurator import Config


def load_with_extends(path, key):
    configs = []
    while path:
        config = Config.from_path(path)
        configs.append(config)
        path = config.get(key)
    config = Config()
    for layer in reversed(configs):
        config.merge(layer)
    config.data.pop(key, None)
    return config
