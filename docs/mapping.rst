Mapping and Merging
===================

.. py:currentmodule:: configurator

.. invisible-code-block: python

  from configurator import Config
  from testfixtures.mock import Mock

Configurator provides flexible tools for combining configuration information from
multiple sources. These are split into two approaches as described below.

Mapping
-------

This is the process of extracting parts of a configuration source and mapping
them into locations in a target :class:`Config`.

Dotted paths
~~~~~~~~~~~~

The most common way of doing this is to use dotted paths for both the source and
target of the mappings. These instruct the mapping machinery to traverse by either
item or attribute access, as appropriate, to deal with the mapping of deeply nested
source arguments to deeply nested target attributes.

For example, suppose we wanted to map these attributes:

>>> mock = Mock()
>>> mock.foo.bar.bob = 42
>>> mock.baz = {'key': 'value'}
>>> del mock.default

To get them into the following config:

>>> config = Config({'cache_size': 13, 'database': {'username': 'test'}})

We could map them in as follows:

>>> config.merge(mock, {
...     'foo.bar.bob': 'cache_size',
...     'baz.key': 'keys.baz',
...     'default.password': 'database.password',
... })
>>> config
configurator.config.Config(
{'cache_size': 42,
 'database': {'username': 'test'},
 'keys': {'baz': 'value'}}
)

As the above example shows:

- If a target container in a traversal path doesn't exist, it will be created as a
  dictionary.
- If any element of a source path does not exist, then the target side of the mapping is
  not performed. If you'd expect an exception to be raised here, see the "Operations"
  section below.

Generative paths
~~~~~~~~~~~~~~~~

If you require even more fine grained control of the mapping process, generative paths can
be used instead of dotted paths. For the example from above, the generative equivalent
would be:

>>> from configurator import Config, source, target
>>> config = Config({'cache_size': 13, 'database': {'username': 'test'}})
>>> config.merge(mock, {
...     source.foo.bar.bob: target['cache_size'],
...     source.baz['key']: target['keys']['baz'],
...     source.default.password: target['database']['password'],
... })
>>> config
configurator.config.Config(
{'cache_size': 42,
 'database': {'username': 'test'},
 'keys': {'baz': 'value'}}
)

The above example shows that this approach is more verbose and explicit, but where it
becomes required is if you need to perform more specific configuration manipulation.

For example, suppose we had this configuration:

>>> config = Config({'actions': ['b', 'c']})

Now we want to merge in this set of actions, to create the final sequence:

>>> empty = Config(['a', 'd'])

Using generative paths, we could map them in like this:

>>> config.merge(source=empty, mapping={
...     source[0]: target['actions'].insert(0),
...     source[-1]: target['actions'].append(),
... })
>>> config
configurator.config.Config({'actions': ['a', 'b', 'c', 'd']})

Generative paths also provide the ability to merge subsections of a config:

>>> config1 = Config({'foo': {'bar': 'baz'}})
>>> config2 = Config({'alpha': 'beta'})
>>> config2.merge(config1, mapping={'foo': target.merge()})
>>> config2
configurator.config.Config({'alpha': 'beta', 'bar': 'baz'})

As you can see, dotted and generative paths can also be used interchangeably.
Generative merging can also be used to merge one config into a section within another:

>>> config1 = Config({'foo': 'bar'})
>>> config2 = Config({'alpha': {'beta': 'gamma'}})
>>> config2.merge(config1, mapping={source: target['alpha'].merge()})
>>> config2
configurator.config.Config({'alpha': {'beta': 'gamma', 'foo': 'bar'}})

.. note::

  When using attribute access in a generative path, this means *only* attribute access:

  >>> config1 = Config({'foo': 'bar'})
  >>> config2 = Config({'alpha': {'beta': 'gamma'}})
  >>> config2.merge(config1, mapping={source: target.alpha.merge()})
  Traceback (most recent call last):
  ...
  AttributeError: 'dict' object has no attribute 'alpha'

  This may result in exceptions being raised when they're used on the target side of a
  mapping, or the source side being treated as not present.

  For this reason, it's better to stick to dotted paths unless you need the specific
  behaviour offered by generative mapping.

Generative paths can also be used to provide literal values on the source:

  >>> from configurator import Config, value
  >>> config = Config()
  >>> config.merge(mapping={value(42): 'version.minor'})
  >>> config
  configurator.config.Config({'version': {'minor': 42}})

Operations
~~~~~~~~~~

Some behaviour is better expressed as a function operating on a mapping path.

required
^^^^^^^^

The default handling of mappings where the source-side is not present is to do nothing,
rather than raising an exception:

>>> Config().merge(source={}, mapping={'foo.bar': 'baz'})

If you need to raise an exception when a source mapping is missing, you can use the
:func:`required` operation:

>>> from configurator import required
>>> Config().merge(source={}, mapping={required('foo.bar'): 'baz'})
Traceback (most recent call last):
...
configurator.path.NotPresent: foo

convert
^^^^^^^

By default, configurator expects data to be of the correct type, with conversion
normally being handled be the parser. Some mapping sources, however, may provide
strings where numbers or booleans are wanted. The :func:`convert` operation can be
used to deal with this:

>>> from configurator import convert
>>> config = Config()
>>> config.merge(source={'MY_ENV_VAR': '2'}, mapping={convert('MY_ENV_VAR', int): 'foo'})
>>> config
configurator.config.Config({'foo': 2})

if_supplied
^^^^^^^^^^^

Some configuration sources provide defaults such as ``None`` or empty strings that are unhelpful
when mapping into a :class:`Config`. In these cases, the mapping can be configured to treat values
as not present if they match Python's definition of "false" by using the :func:`if_supplied`
operation:

>>> from argparse import Namespace
>>> from configurator import if_supplied
>>> config = Config()
>>> config.merge(source=Namespace(my_option=None), mapping={if_supplied('my_option'): 'some_key'})
>>> config
configurator.config.Config({})

Merging
--------

This is the process of combining two :class:`Config` objects.
By default, this involves unioning dictionaries and concatenating lists:

>>> config1 = Config({'dict': {'a': 1, 'b': 2}, 'list': ['a', 'b']})
>>> config2 = Config({'dict': {'b': 3, 'c': 4}, 'list': ['c', 'd']})
>>> config1 + config2
configurator.config.Config({'dict': {'a': 1, 'b': 3, 'c': 4}, 'list': ['a', 'b', 'c', 'd']})

Merging is performed using a configurable mapping of python types to merge functions.
This can be augmented or completely replaced by using the :meth:`~Config.merge` method.

For example, if we wished to support :class:`tuple` merging by concatenation, we could
re-use the merge function for lists:

>>> from configurator.merge import default_mergers, merge_list
>>> config1 = Config(('a', 'b'))
>>> config2 = Config(('c', 'd'))
>>> config1.merge(config2, mergers=default_mergers+{tuple: merge_list})
>>> config1
configurator.config.Config(('a', 'b', 'c', 'd'))

The :attr:`default_mergers` mapping supports addition to make it easy to add extra
merge functions to the existing ones. If, instead, you want to completely replace
the mapping, you can use a normal :class:`dict`:

>>> config1 = Config({'tuple': ('a', 'b')})
>>> config2 = Config({'tuple': ('c', 'd')})
>>> config1.merge(config2, mergers={tuple: merge_list})
Traceback (most recent call last):
...
TypeError: Cannot merge <class 'dict'> with <class 'dict'>

As you can see, this does mean that any merging that isn't catered for will result in a
:class:`TypeError` being raised.

When writing a merge function, the ``context`` parameter is there so that merging of
complex data types can be handed off to be handled by whatever is the most appropriate
merge function. This is only likely to be needed when merging mappings, and that
has already been implemented, but should you need to do this, please consult the
source code for :func:`configurator.merge.merge_dict`.
