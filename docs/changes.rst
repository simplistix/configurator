.. py:currentmodule:: configurator

Changes
=======

2.5.0 (1 Jun 2020)
------------------

- Move the code for the "Config file that extends another config file" pattern into
  a helper function in :func:`configurator.patterns.load_with_extends`.

2.4.0 (31 May 2020)
-------------------

- Allow the list of values considered false by :meth:`if_supplied` to be specified.

- :meth:`if_supplied` no longer considers ``False`` to be false, as when present, that's
  often an explicitly provided value.

2.3.0 (27 May 2020)
-------------------

- :class:`Config` instances can now be pickled.

2.2.0 (25 May 2020)
-------------------

- :func:`value` has been added to allow literal values to be used in the left
  side of mappings passed to :meth:`Config.merge`.

2.1.0 (25 May 2020)
-------------------

- Configuration values my now be set using attribute or item setting on
  :class:`~.node.ConfigNode` instances.

- :meth:`~.node.ConfigNode.node` can be used to obtain or create a
  :class:`~.node.ConfigNode` from a dotted path and will give you a node even
  for a value of a :class:`dict` or item in a :class:`list`.

- :class:`~.node.ConfigNode` instances now have a :meth:`~.node.ConfigNode.set`
  method that can be used to replace the value of that part of the configuration,
  regardless of whether it is a container, list item or dictionary value.

2.0.0 (15 Apr 2020)
-------------------

- Performance improvements when import parsers.

- Removed the ability to provide new parsers using `pkg_resources`
  entry points.

1.3.0 (29 Jan 2020)
-------------------

- Add :meth:`Config.from_env` class method to help with extacting
  large numbers of environment variables into configuration.

1.2.0 (29 May 2019)
-------------------

- Enable the context manager returned by :meth:`Config.push` to return
  the state of a global config object to what it was before :meth:`~Config.push`
  was called.

1.1.0 (29 May 2019)
-------------------

- Add support for :meth:`pushing <Config.push>` and :meth:`popping <Config.pop>`
  config data onto a global :class:`Config`.

1.0.0 (4 Apr 2019)
------------------

- Support for optional configuration files in :meth:`Config.from_path`.

- Add :meth:`if_supplied` mapping operation.

- Fully documented.

0.5.0 (15 Mar 2019)
---------------------

- Initial release without docs.

