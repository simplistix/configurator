
configurator
============

|CircleCI|_  |Docs|_

.. |CircleCI| image:: https://circleci.com/gh/simplistix/configurator/tree/master.svg?style=shield
.. _CircleCI: https://circleci.com/gh/simplistix/configurator/tree/master

.. |Docs| image:: https://readthedocs.org/projects/configurator/badge/?version=latest
.. _Docs: http://configurator.readthedocs.org/en/latest/

This is a Python library for building a configuration store
from one or more layered configuration sources.
These are most commonly files, with yaml, toml and json support included
and other formats easily supported with plugins.

It provides an easy interface for accessing configuration information
sourced from overlaid config files or mapped in from environment variables
or command line options.

Configuration information is also available as nested, simple python data types so that
you can validate the schema of your configuration using the tool of your choice.

Quickstart
~~~~~~~~~~

.. invisible-code-block: python

    fs.create_file('/etc/my_app/config.yaml',
                   contents='cache:\n  location: /var/my_app/\n')
    fs.create_dir('/var/logs/myapp/')
    replace('os.environ.MYAPP_THREADS', '2', strict=False)
    replace('os.environ.MYAPP_CACHE_DIRECTORY', '/var/logs/myapp/', strict=False)
    replace('sys.argv', ['myapp.py', '--threads', '3', '--max-files', '200'])
    from pprint import pprint

To install the library, go for:

.. code-block:: bash

  pip install configurator[yaml,toml]

Here's how you would handle a layered set of defaults, system-wide config
and then optional per-user config:

.. code-block:: python


    from configurator import Config

    defaults = Config({
        'cache': {
            'location': '/tmp/my_app',
            'max_files': 100,
        },
        'banner': 'default banner',
        'threads': 1,
    })
    system = Config.from_path('/etc/my_app/config.yaml')
    user = Config.from_path('~/.my_app.yaml', optional=True)
    config = defaults + system + user

Now, if we wanted configuration from the environment and command line
arguments to override those provided in configuration files, we could do so
as follows:

.. code-block:: python

    import os
    from argparse import ArgumentParser
    from configurator import convert, target, required

    config.merge(os.environ, {
        convert('MYAPP_THREADS', int): 'threads',
        required('MYAPP_CACHE_DIRECTORY'): 'cache.location',
    })

    parser = ArgumentParser()
    parser.add_argument('--threads', type=int)
    parser.add_argument('--max-files', type=int)
    args = parser.parse_args()

    config.merge(args, {
        'threads': 'threads',
        'max_files': 'cache.max_files',
    })

To check the configuration we've accumulated is sensible we can use a data validation library
such as `Voluptuous`__:

__ https://github.com/alecthomas/voluptuous

.. code-block:: python

    from os.path import exists
    from voluptuous import Schema, All, Required, PathExists

    schema = Schema({
        'cache': {'location': All(str, PathExists()), 'max_files': int},
        'banner': Required(str),
        'threads': Required(int),
        })

    schema(config.data)

So, with all of the above, we could use the following sources of configuration:

>>> import os, sys
>>> print(open('/etc/my_app/config.yaml').read())
cache:
  location: /var/my_app/
<BLANKLINE>
>>> os.environ['MYAPP_THREADS']
'2'
>>> os.environ['MYAPP_CACHE_DIRECTORY']
'/var/logs/myapp/'
>>> sys.argv
['myapp.py', '--threads', '3', '--max-files', '200']

With the above sources of configuration, we'd end up with a configuration store that we can use as
follows:

>>> config.cache.location
'/var/logs/myapp/'
>>> config.cache.max_files
200
>>> config.banner
'default banner'
>>> config.threads
3
