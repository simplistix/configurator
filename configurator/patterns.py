from . import Config


def load_with_extends(path, key='extends', root=None):
    """
    Helper for the :ref:`"extends" <extends-pattern>` pattern.

    :param path:
      The path of the configuration file to start with.
    :param key:
      The key to use to indicate that another file should be used as a base.
    :param root:
      If supplied, configuration is extracted from this key at the root of
      each configuration file that is loaded, provided it is present. If missing
      from any file, the whole configuration from that file is used instead.
    """
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
