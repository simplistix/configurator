"""
Helpers for specific patterns of usage.
"""

from . import Config


def load_with_extends(path, key, root=None):
    configs = []
    while path:
        config = Config.from_path(path)
        if root is not None and root in config:
            config = config[root]
        configs.append(config)
        path = config.get(key)
    config = Config()
    for layer in reversed(configs):
        config.merge(layer)
    config.data.pop(key, None)
    return config
