.. py:currentmodule:: configurator

Using Configurator
==================

This document goes into more detail than the quickstart and should cover enough
functionality for most use cases. For examples of how to use this functionality,
see :doc:`patterns`.

Installation
~~~~~~~~~~~~

Configurator is available on the `Python Package Index`__ and can be installed
with any tools for managing Python environments. The package has no hard
dependencies beyond the standard library, but you will need extra libraries for most
file formats from which you may want to read configuration information. As a result,
you may wish to install Configurator with the appropriate extra requirement to meet
your needs:

.. code-block:: bash

  pip install configurator[toml]
  pip install configurator[yaml]


__ https://pypi.org

Getting configuration information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. invisible-code-block: python

    fs.create_file('/etc/myapp.yml',
                   contents='myapp:\n  cache:\n    location: /var/my_app/\n')


The most common source of configuration information is reading from files.
Given a file such as this:

>>> print(open('/etc/myapp.yml').read())
myapp:
  cache:
    location: /var/my_app/
<BLANKLINE>

A :class:`Config` object can be obtained as follows:

>>> from configurator import Config
>>> Config.from_path('/etc/myapp.yml')
configurator.config.Config({'myapp': {'cache': {'location': '/var/my_app/'}}})

If you already have an open stream, it woud be this instead:

>>> with open('/etc/myapp.yml') as source:
...     Config.from_stream(source)
configurator.config.Config({'myapp': {'cache': {'location': '/var/my_app/'}}})

Finally, if you have the text source in memory, you would do the following:

>>> text = """
...   cache:
...     location: /var/my_app/
... """
>>> Config.from_text(text, 'yaml')
configurator.config.Config({'cache': {'location': '/var/my_app/'}})

Note that because we have no way of guessing, the parser must be specified.
The ``parser`` parameter can also be used with :meth:`Config.from_path` and
:meth:`Config.from_stream` to explicitly specify a parser, regardless of the name of
the file.

The parser can also be specified as a callable, if you have one-off unusual parsing needs:

>>> text = """
... {'format': 'not json'}
... """
>>> import ast
>>> def python(stream):
...     return ast.literal_eval(stream.read())
>>> Config.from_text(text, python)
configurator.config.Config({'format': 'not json'})

If you need to add support for a new config file format, see :doc:`parsers`.

It is also quite normal to instantiate a :class:`Config` and then :doc:`merge <mapping>`
configuration into it from several other sources:

>>> Config()
configurator.config.Config({})

If you already have a deserialized source of configuration information, you can
wrap a :class:`Config` around it and use it from that point onwards:

.. invisible-code-block: python

    import requests
    from testfixtures.mock import Mock
    requests = Mock()
    requests.get.return_value.json.return_value = {'cache': {'location': '/var/my_app/'}}
    replace('sys.modules.requests', requests, strict=False)

>>> Config(requests.get('http://config-store/myapp.json').json())
configurator.config.Config({'cache': {'location': '/var/my_app/'}})

Accessing configuration information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configurator aims to provide access to configuration information in a simple and
natural way, similar to the underlying python data structures but allowing both
item and attribute access to be used interchangeably.

So, with a config such as this:

>>> config = Config({'logs': '/var/my_app/',
...                  'sources': [{'url': 'http://example.com/1',
...                               'username': 'user1',
...                               'password': 'p1'},
...                              {'url': 'http://example.com/2',
...                               'username': 'user2',
...                               'password': 'p2'}]})

The various parts can be accessed as follows:

>>> config.logs
'/var/my_app/'
>>> for source in config.sources:
...     print(source.url, source.username, source.password)
http://example.com/1 user1 p1
http://example.com/2 user2 p2

Item access can also be used, if preferred:

>>> config['sources'][1]['url']
'http://example.com/2'

Where it's more natural, configuration can also be treated like a dictionary.
For example, with this config:

>>> config = Config({'databases': {'main': 'mysql://foo@bar/main',
...                                'backup': 'mysql://baz@bob/backup'},
...                  'priority': ['main', 'backup']})

You could iterate through the databases as follows:

>>> for name, url in sorted(config.databases.items()):
...     print(name, url)
backup mysql://baz@bob/backup
main mysql://foo@bar/main

Likewise, if a key may not be present:

>>> config.databases.get('read_only', default=config.databases.get('backup'))
'mysql://baz@bob/backup'

As a fallback, every node in the config will have a :attr:`~node.ConfigNode.data` attribute
that can be used to get hold of the underlying configuration information:

>>> config.priority.data
['main', 'backup']

Combining sources of configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's rare that configuration for an application will come from a single source and
so configurator makes it easy to combine them.

The simplest way is by adding two :class:`Config` instances. This will recursively
merge the underlying configuration data, unioning dictionary items and concatenating
sequences:

>>> config1 = Config({'mapping': {'a': 1, 'b': 2}, 'sequence': ['a']})
>>> config2 = Config({'mapping': {'b': 3, 'c': 4}, 'sequence': ['b']})
>>> config1 + config2
configurator.config.Config({'mapping': {'a': 1, 'b': 3, 'c': 4}, 'sequence': ['a', 'b']})

If you need to have more control over this process, :meth:`Config.merge` allows
you to specify how merging will be performed per python object type:

>>> config1 = Config([1, 2, 3, 4, 5])
>>> config2 = Config([6, 7, 8, 9, 10])

>>> from configurator import default_mergers
>>> from itertools import chain, zip_longest
>>> def alternate(context, source, target):
...     return [i for i in chain.from_iterable(zip_longest(target, source)) if i]

>>> config1.merge(config2, mergers=default_mergers+{list: alternate})
>>> config1
configurator.config.Config([1, 6, 2, 7, 3, 8, 4, 9, 5, 10])

.. note::
  :meth:`~Config.merge` mutates the :class:`Config` on which it is called
  while addition leaves both of the source configs unmodified and returns a
  new :class:`Config`.

.. invisible-code-block: python

    from testfixtures.mock import Mock
    import os
    replace('os.environ.BAZ', 'True', strict=False)

If you need more flexibility in how parts of the configuration source are mapped in,
or if the source data structure is not compatible with merging, you can use a mapping:

>>> source = Mock()
>>> source.foo.bar = 'some_value'

>>> config = Config({'bar': {'type': 'foo'}, 'baz': False})
>>> config.merge(source, {'foo.bar': 'bar.name'})

>>> from configurator.mapping import convert
>>> from ast import literal_eval
>>> config.merge(os.environ, {convert('BAZ', literal_eval): 'baz'})

>>> config
configurator.config.Config({'bar': {'name': 'some_value', 'type': 'foo'}, 'baz': True})

There is a lot of flexibility in how mapping and merging can be performed. For
detailed documentation on this see :doc:`mapping`.

.. invisible-code-block: python

    fs.create_file('/etc/my_app/config.yaml', contents="""
      actions:
        - checkout:
            repo: git@github.com:Simplistix/configurator.git
            branch: master
        - run: "cat /foo/bar"
      """)

One other form of manipulation that's worth mentioning is when incoming data isn't
quite the right shape. Take this YAML:

>>> print(open('/etc/my_app/config.yaml').read())
<BLANKLINE>
  actions:
    - checkout:
        repo: git@github.com:Simplistix/configurator.git
        branch: master
    - run: "cat /foo/bar"
<BLANKLINE>

The actions, while easy to read, aren't homogeneous or easy for the application to use.
It might be easier if they were something like:

.. code-block:: python

  {'actions': [{'type': 'checkout', 'kw': {'repo': '...', 'branch': 'master'}},
               {'type': 'run', 'args': ('cat /foo/var',)}]}

We can achieve this by modifying the data in the :class:`Config` programmatically
with a function such as this:

.. code-block:: python

    def normalise(data):
        actions = []
        for action_data in data:
            (type_, params), = action_data.items()
            if isinstance(params, dict):
                actions.append({'type': type_, 'args': (), 'kw': params})
            else:
                actions.append({'type': type_, 'args': (params,), 'kw': {}})
        data[:] = actions

This can be applied to the raw config as follows:

>>> config = Config.from_path('/etc/my_app/config.yaml')
>>> normalise(config.actions.data)

.. invisible-code-block: python

    from testfixtures.mock import MagicMock
    action_handlers = MagicMock()

Now, the application code can use the config in a uniform way:

>>> for action in config.actions:
...     output = action_handlers[action.type](*action.args, **action.kw.data)
