.. py:currentmodule:: configurator

Using Configurator
==================

This document goes into more detail than the quickstart and should cover enough
functionality for most use cases. For examples of how to use this functionality,
see :doc:`patterns`. For details of all the classes, methods and functions available, see
the :doc:`api`.

Getting configuration information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Several ways of obtaining configuration information are available.

Files, streams and text
-----------------------

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

If you already have an open stream, it would be this instead:

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

When parsing strings, the parser must be specified because we have no way of guessing.
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

If you need to add support for a new config file format or wish to use a different parser
for existing file formats, see :ref:`parsers`.

Environment variables
---------------------

Configuration can be obtained from environment variables, the best approach depends on the
number and type of variables you're starting from.

If it's a small number and you need to add them do arbitrary configuration locations,
then :doc:`mapping <mapping>` works well:

.. invisible-code-block: python

    replace('os.environ.OMP_NUM_THREADS', '2', strict=False)
    replace('os.environ.CACHE_DIRECTORY', '/var/cache/it/', strict=False)
    import os

>>> from configurator import Config, convert, required
>>> config = Config()
>>> config.merge(os.environ, {
...     convert('OMP_NUM_THREADS', int): 'threads',
...     required('CACHE_DIRECTORY'): 'cache.location',
... })
>>> config
configurator.config.Config({'cache': {'location': '/var/cache/it/'}, 'threads': 2})

If you have many environment variables with the same prefix, :meth:`Config.from_env`
can be used:

.. invisible-code-block: python

    replace('os.environ', {
        'MYAPP_THREADS': '2',
        'MYAPP_CACHE_DIRECTORY': '/var/logs/myapp/'
    })

>>> os.environ['MYAPP_THREADS']
'2'
>>> os.environ['MYAPP_CACHE_DIRECTORY']
'/var/logs/myapp/'
>>> Config.from_env('MYAPP_')
configurator.config.Config({'cache_directory': '/var/logs/myapp/', 'threads': '2'})

If the environment variables contain patterns that indicate their type as a suffix, then
:meth:`~Config.from_env` can do the type conversion:

.. invisible-code-block: python

    replace('os.environ', {
        'MYAPP_SERVER_PORT': '4242',
        'MYAPP_CACHE_PATH': '/tmp/myapp'
    })

For example, given the following environment variables:

>>> os.environ.get('MYAPP_SERVER_PORT')
'4242'
>>> os.environ.get('MYAPP_CACHE_PATH')
'/tmp/myapp'

Configuration could be extracted as follows:

>>> from pathlib import Path
>>> Config.from_env(prefix='MYAPP_', types={'PORT': int, 'PATH': Path})
configurator.config.Config({'cache_path': PosixPath('/tmp/myapp'), 'server_port': 4242})

If different prefixes indicate different configuration locations, then ``prefix`` can be
a mapping:


.. invisible-code-block: python

    replace('os.environ', {
        'MYAPP_POSTGRES_HOST': 'some-host',
        'MYAPP_POSTGRES_PORT': '5432',
        'MYAPP_REDIS_HOST': 'other-host',
        'MYAPP_REDIS_PORT': '6379',
    })

>>> os.environ.get('MYAPP_POSTGRES_HOST')
'some-host'
>>> os.environ.get('MYAPP_POSTGRES_PORT')
'5432'
>>> os.environ.get('MYAPP_REDIS_HOST')
'other-host'
>>> os.environ.get('MYAPP_REDIS_PORT')
'6379'
>>> Config.from_env(prefix={
...     'MYAPP_POSTGRES_': 'services.postgres',
...     'MYAPP_REDIS_': 'services.redis'
... })
configurator.config.Config(
{'services': {'postgres': {'host': 'some-host', 'port': '5432'},
              'redis': {'host': 'other-host', 'port': '6379'}}}
)


Other sources
-------------

It is also quite normal to instantiate an empty :class:`Config` and then :doc:`merge <mapping>`
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
...                  'sources': [{'url': 'https://example.com/1',
...                               'username': 'user1',
...                               'password': 'p1'},
...                              {'url': 'https://example.com/2',
...                               'username': 'user2',
...                               'password': 'p2'}]})

The various parts can be accessed as follows:

>>> config['logs']
'/var/my_app/'
>>> for source in config['sources']:
...     print(source['url'], source['username'], source['password'])
https://example.com/1 user1 p1
https://example.com/2 user2 p2

Using item access allows configuration that contains both mappings and sequences to be
traversed easily and reliably:

>>> config['sources'][1]['url']
'https://example.com/2'

Where it's more natural, configuration can also be treated like a dictionary.
For example, with this config:

>>> config = Config({'databases': {'main': 'mysql://foo@bar/main',
...                                'backup': 'mysql://baz@bob/backup'}})

You could iterate through the databases as follows:

>>> for name, url in sorted(config['databases'].items()):
...     print(name, url)
backup mysql://baz@bob/backup
main mysql://foo@bar/main

Likewise, if a key may not be present:

>>> config['databases'].get('read_only', default=config['databases'].get('backup'))
'mysql://baz@bob/backup'

As a convenience, attribute access may also be used where possible.
So, with a config such as this:

>>> config = Config({'sources': [{'url': 'https://example.com/1',
...                               'username': 'user1',
...                               'password': 'p1'},
...                              {'url': 'https://example.com/2',
...                               'username': 'user2',
...                               'password': 'p2'}]})

You could take advantage of attribute access as follows:

>>> for source in config.sources:
...     print(source.username, source.password)
user1 p1
user2 p2

.. warning::

  Care must be taken when using attribute access as methods and attributes provided by
  configurator will take precedence over any configuration information.

As a fallback, every node in the config will have a :attr:`~node.ConfigNode.data` attribute
that can be used to get hold of the underlying configuration information:

>>> type(config.sources)
<class 'configurator.node.ConfigNode'>
>>> type(config.sources.data)
<class 'list'>
>>> len(config.sources.data)
2

.. warning::
  :attr:`~node.ConfigNode.data` should not be modified as problems will occur
  if the :class:`~node.ConfigNode` hierarchy and :attr:`~node.ConfigNode.data`
  hierarchy become out of sync.

If you want to have a :class:`~node.ConfigNode` even in the case of scalar values, then the
:meth:`~node.ConfigNode.node` method can be used:

>>> config = Config({'x': 1})
>>> config.node('x')
configurator.node.ConfigNode(1)

Combining sources of configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's rare that configuration for an application will come from a single source and
so configurator makes it easy to combine them.

Simple overlaying
-----------------

The simplest way is by adding two :class:`Config` instances. This will recursively
merge the underlying configuration data, unioning dictionary items and concatenating
sequences:

>>> config1 = Config({'mapping': {'a': 1, 'b': 2}, 'sequence': ['a']})
>>> config2 = Config({'mapping': {'b': 3, 'c': 4}, 'sequence': ['b']})
>>> config1 + config2
configurator.config.Config({'mapping': {'a': 1, 'b': 3, 'c': 4}, 'sequence': ['a', 'b']})

Merging
-------

If you need to have more control over this process, :meth:`Config.merge` allows
you to specify how merging will be performed per python object type:

>>> config1 = Config([1, 2, 3, 4, 5])
>>> config2 = Config([6, 7, 8, 9, 10])

In this case, we want to interleave the two lists when they are merged, which can be done
with a function like this:

.. code-block:: python

    from itertools import chain, zip_longest

    def alternate(context, source, target):
        return [i for i in chain.from_iterable(zip_longest(target, source)) if i]

We can use this with the :any:`default_mergers` to ensure that all list that are merged
are interleaved:

>>> from configurator import default_mergers
>>> config1.merge(config2, mergers=default_mergers+{list: alternate})
>>> config1
configurator.config.Config([1, 6, 2, 7, 3, 8, 4, 9, 5, 10])

.. note::
  :meth:`~Config.merge` mutates the :class:`Config` on which it is called
  while adding two :class:`Config` objects together leaves both of the source configs unmodified
  and returns a new :class:`Config`.

.. invisible-code-block: python

    from testfixtures.mock import Mock
    import os
    replace('os.environ.BAZ', 'True', strict=False)

For more detailed documentation, see :doc:`mapping`.

Mapping
-------

If you need more flexibility in how parts of the configuration source are mapped in,
or if the source data structure is not compatible with merging, you can use a mapping:

>>> source = Mock()
>>> source.foo.bar = 'some_value'
>>> config = Config({'bar': {'type': 'foo'}})
>>> config.merge(source, {'foo.bar': 'bar.name'})
>>> config
configurator.config.Config({'bar': {'name': 'some_value', 'type': 'foo'}})

Mapping can also be used to convert data from a configuration source:

>>> from configurator.mapping import convert
>>> from ast import literal_eval
>>> os.environ.get('BAZ')
'True'
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

Modifying configuration
~~~~~~~~~~~~~~~~~~~~~~~

Once you have a :class:`Config` object, you may still need to modify the configuration
information it contains.

Adding and deleting
-------------------

Items can be added to a config using the mapping interface:

>>> config = Config()
>>> config['meaning'] = 42
>>> config
configurator.config.Config({'meaning': 42})

If the name is compatible with Python syntax, then you can also use attribute assignment:

>>> config.meaning = 'new'
>>> config
configurator.config.Config({'meaning': 'new'})

If you need to remove an item, then you can do this using the mapping interface:

>>> del config['meaning']
>>> config
configurator.config.Config({})

If the name is compatible with Python syntax, then you can also use the attribute interface:

>>> config = Config({'meaning': 'life'})
>>> del config.meaning
>>> config
configurator.config.Config({})

If the configuration is a list, then modifying items can be done using the sequence interface:

>>> config = Config(['item1', 'item2', 'item3'])
>>> config[0] = 'new'
>>> config
configurator.config.Config(['new', 'item2', 'item3'])

This can also be used to remove items:

>>> del config[1]
>>> config
configurator.config.Config(['new', 'item3'])

If you need to set an item deep within a nesting that may or may not exist, then
:meth:`~node.ConfigNode.node` can be used:

>>> config = Config({'foo': {}})
>>> config.node('foo.bar.baz', create=True).set(42)
>>> config
configurator.config.Config({'foo': {'bar': {'baz': 42}}})

If the location traverses through lists, then a :class:`~configurator.path.Path` starting
from :any:`source <configurator.source>` can be used:

>>> from configurator import source
>>> config = Config([{'name': 'db1', 'password': 'compromised'}])
>>> config.node(source[0]['password']).set('secure')
>>> config
configurator.config.Config([{'name': 'db1', 'password': 'secure'}])

Pushing and popping
-------------------

Some frameworks and patterns make use of a global configuration object which needs to be referenced
before the configuration is obtained from its sources. For this reason, Configurator provides the
facility to push configuration onto an existing :class:`Config` and later pop it off.

For example, given this global config:

>>> config = Config({'option1': 'default', 'option3': 'foo'})

Additional configuration can be pushed onto it once available:

>>> config.push(Config({'option1': 'non-default', 'option2': 42}))
<configurator.config.PushContext object at ...>
>>> config
configurator.config.Config({'option1': 'non-default', 'option2': 42, 'option3': 'foo'})

If that configuration is no longer relevant, it can be popped off:

>>> config.pop()
>>> config
configurator.config.Config({'option1': 'default', 'option3': 'foo'})

This process can also be used for managing a context:

>>> with config.push(Config({'option1': 'non-default'})):
...     print(config['option1'])
non-default

If you wish to push an entirely new configuration, this can be done as follows:

>>> config = Config({'option1': 'default', 'option3': 'foo'})
>>> with config.push(Config({'option1': 'non-default', 'option2': 42}), empty=True):
...     print(config)
configurator.config.Config({'option1': 'non-default', 'option2': 42})

You can also use this method to preserve configuration and restore it to its previous state
as follows:

>>> config = Config({'option1': 'default', 'option3': 'foo'})
>>> with config.push():
...     config['option1'] = 'bad'
...     del config['option3']
>>> config
configurator.config.Config({'option1': 'default', 'option3': 'foo'})

Cloning
-------

If you need a complete and separate copy of a :class:`Config` for any reason, one can be
obtained using the :meth:`~Config.clone` method:

>>> original = Config({'x': {'y': 'z'}})
>>> scratch = original.clone()
>>> scratch['a'] = 'b'
>>> scratch.node('x.y').set('z-')
>>> scratch
configurator.config.Config({'a': 'b', 'x': {'y': 'z-'}})
>>> original
configurator.config.Config({'x': {'y': 'z'}})

Transforming
------------

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

    def normalise(actions):
        for action in actions:
            (type_, params), = action.data.items()
            if isinstance(params, dict):
                data = {'type': type_, 'args': (), 'kw': params}
            else:
                data = {'type': type_, 'args': (params,), 'kw': {}}
            action.set(data)

This can be applied to the raw config as follows:

>>> config = Config.from_path('/etc/my_app/config.yaml')
>>> normalise(config.actions)

.. invisible-code-block: python

    from testfixtures.mock import MagicMock
    action_handlers = MagicMock()

Now, the application code can use the config in a uniform way:

>>> for action in config.actions:
...     output = action_handlers[action.type](*action.args, **action.kw.data)

.. _parsers:

Adding new parsers
~~~~~~~~~~~~~~~~~~

.. py:currentmodule:: configurator

When creating :class:`Config` instances using :meth:`~Config.from_text`,
:meth:`~Config.from_stream` or :meth:`~Config.from_path` you may have to specify a parser.
This can be either a string or a callable.

When it's a callable, which should be rare, the callable should take a single argument
that will be the stream from which text can be read. A nested python data structure
containing the parsed results of the stream should be returned, made up of only simple python
data types as would be returned by :func:`ast.literal_eval`.

More commonly, it will either be deduced from the extension of the file being processed or
can be provided as a textual file extension such as ``'yaml'``, ``'toml'`` or ``'json'``.
Where these require third party libraries, you may need to install extras for them to be
available:

.. code-block:: bash

  pip install configurator[yaml,toml]
