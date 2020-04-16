Adding new parsers
==================

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
