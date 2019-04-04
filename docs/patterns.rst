Patterns of Use
===============

The rest of the documentation explains how Configurator works in abstract, while
the sections below provide concrete examples of how it can be used in various
applications.

.. invisible-code-block: python

    # help pyfakefs out...
    import os
    replace('os.environ.HOME', '/home/some_user', strict=False)
    replace('configurator.config.exists', os.path.exists)

Layered config files
--------------------

A common pattern is to have a system-wide configuration file, overlaid with
an optional user-specific config file. For example:

.. topic:: /etc/my_app.yml
 :class: write-file

 ::

   data_path: /var/wherever
   logging_level: warning
   foo_enabled: false

.. topic:: /home/some_user/.my_app.yml
 :class: write-file

 ::

   logging_level: debug
   foo_enabled: true

This could be loaded with a function such as this:

.. code-block:: python

    from configurator import Config

    def load_config():
        base = Config.from_path('/etc/my_app.yml')
        user = Config.from_path('~/.my_app.yml', optional=True)
        return base + user

Using the two example config files would result in this config:

>>> load_config()
configurator.config.Config(
{'data_path': '/var/wherever',
 'foo_enabled': True,
 'logging_level': 'debug'}
)

Config file that extends another config file
--------------------------------------------

With this pattern, config files use a key to explicitly specify another config
file that they extend. For example:

.. topic:: base.yml
 :class: write-file

 ::

   data_path: /var/wherever
   logging_level: warning
   foo_enabled: false

.. topic:: my_app.yml
 :class: write-file

 ::

   extends: base.yml
   logging_level: debug
   foo_enabled: true

This could be loaded with a function such as this:

.. code-block:: python

    from configurator import Config

    def load_config(path):
        configs = []
        while path:
            config = Config.from_path(path)
            configs.append(config)
            path = config.get('extends')
        config = Config()
        for layer in reversed(configs):
            config.merge(layer)
        config.data.pop('extends')
        return config

Using the two example config files would result in this config:

>>> load_config('my_app.yml')
configurator.config.Config(
{'data_path': '/var/wherever',
 'foo_enabled': True,
 'logging_level': 'debug'}
)

Config files that include other config files
--------------------------------------------

Another common pattern is to have an application-wide configuration
file that includes sections of configuration from files to be found
in a particular directory. For example:

.. topic:: /etc/myapp.yml
 :class: write-file

 ::

    logging_level: warning

.. topic:: /etc/myapp.d/site1.yaml
 :class: write-file

 ::

   domain: site1.example.com
   root: /var/sites/site1

.. topic:: /etc/myapp.d/site2.yaml
 :class: write-file

 ::

   domain: site2.example.com
   root: ~someuser/site2

This could be loaded with a function such as this:

.. code-block:: python

    from configurator import Config, source, target
    from glob import glob

    def load_config():
        config = Config({'sites': []})
        config.merge(Config.from_path('/etc/myapp.yml'))
        for path in glob('/etc/myapp.d/*.y*ml'):
            config.merge(Config.from_path(path), mapping={source: target['sites'].append()})
        return config

Using the example config files above would result in this config:

>>> load_config()
configurator.config.Config(
{'logging_level': 'warning',
 'sites': [{'domain': 'site1.example.com',
            'root': '/var/sites/site1'},
           {'domain': 'site2.example.com',
            'root': '~someuser/site2'}]}
)

Config file overlaid with environment variables
-----------------------------------------------

Environment variables provide a way to inject configuration into an application.
This can often be to override configuration from a file but doesn't easily fit
the schema of a config file. Environment variables are also hindered by the fact that
they only natively able to have string values.

.. invisible-code-block: python

    replace('os.environ.MYAPP_ENABLED', 'True', strict=False)
    replace('os.environ.MYAPP_THREADS', '13', strict=False)

The mapping process Configurator offers can help with both of these problems.
For example:

.. topic:: myapp.yml
 :class: write-file

 ::

    enabled: false
    threads: 1

The environment variables below can be mapped into the config file above.

>>> os.environ.get('MYAPP_ENABLED')
'True'
>>> os.environ.get('MYAPP_THREADS')
'13'

This could be done with a function such as this:

.. code-block:: python

    from configurator import Config, convert
    from ast import literal_eval
    import os

    def load_config():
        config = Config.from_path('myapp.yml')
        config.merge(os.environ, mapping={
            convert('MYAPP_ENABLED', literal_eval): 'enabled',
            convert('MYAPP_THREADS', int): 'threads',
        })
        return config

Using the example config files above would result in this config:

>>> load_config()
configurator.config.Config({'enabled': True, 'threads': 13})

Config file with command line overrides
---------------------------------------

Many applications allow you to specify the config file on the command line as well
as options that override some of the file based configuration.

For example, command line arguments could be parsed by a function such as this:

.. code-block:: python

    from argparse import ArgumentParser, FileType

    def parse_args():
        parser = ArgumentParser()
        parser.add_argument('config', type=FileType('r'))
        parser.add_argument('--verbose', action='store_true')
        parser.add_argument('--threads', type=int)
        return parser.parse_args()

These arguments can be merged into the config they specify with a function such as thing:

.. code-block:: python

    from configurator import Config, convert, if_supplied

    def verbose_to_level(verbose):
        if verbose:
            return 'debug'

    def load_config(args):
        config = Config.from_stream(args.config)
        config.merge(args, mapping={
            convert('verbose', verbose_to_level): 'log_level',
            if_supplied('threads'): 'threads',
        })
        return config

So, given these command line arguments:

.. invisible-code-block: python

    replace('sys.argv', ['myapp.py', 'myapp.yaml', '--verbose'])
    import sys

>>> sys.argv
['myapp.py', 'myapp.yaml', '--verbose']

Along with a config file such as this:

.. topic:: myapp.yaml
 :class: write-file

 ::

    log_level: warning
    threads: 1

The two functions above would produce the following config:

>>> args = parse_args()
>>> load_config(args)
configurator.config.Config({'log_level': 'debug', 'threads': 1})

Application and framework configuration in the same file
--------------------------------------------------------

It can make sense for an application and the framework it's built with to make use of the
same config file, particularly when combined with layered config files, as described above. This can
allow all applications on a system to share a basic default config while providing overrides to
that configuration along with their own configuration in an application-specific config file.

What makes this work is keeping the application and framework configuration in separate top-level
namespaces. For example:

.. topic:: myapp.yml
 :class: write-file

 ::

    # framework configuration:
    logging:
        console_level: false
        file_level: warning

    # application configuration, containing within one top-level key:
    my_app:
        enabled: True
        threads: 1

Configuring the framework and application then becomes dispatching the top-level config
sections appropriately:

.. invisible-code-block: python

    def configure_framework(app, logging):
        print('TheFramework running %s(%r)\nlogging: %r>' % (type(app).__name__, vars(app), logging))

.. code-block:: python

    from configurator import Config

    class MyApp:
        def __init__(self, enabled, threads):
            self.enabled, self.threads = enabled, threads

    def build_app(config_path):
        config = Config.from_path(config_path)
        app = MyApp(**config.data.pop('my_app'))
        return configure_framework(app, **config.data)

Combining the above function and configuration file might result in:

>>> build_app('myapp.yml')
TheFramework running MyApp({'enabled': True, 'threads': 1})
logging: {'console_level': False, 'file_level': 'warning'}>
