============
Configurator
============

This is a Python library for building a configuration object
from one or more `YAML`__ files validated using a `schema`__.

The intent is to support:

- overlaid files, such as a system-wide config, a per user config and an
  application config.

- nested files, where configuration is built up by loading files into
  points in the config tree.

- application plugins, where parts of a configuration take their schema from
  plugins and can only be understood by those plugins.

__ http://pyyaml.org/
__ https://pypi.python.org/pypi/voluptuous

The latest documentation can be found at:
http://configurator.readthedocs.org/en/latest/

Development takes place here:
https://github.com/Simplistix/configurator/
