API Reference
=============

Configuration
-------------

.. autoclass:: configurator.Config
   :members:
   :member-order: bysource
   :show-inheritance:
   :special-members:
   :exclude-members: __weakref__, __init__


.. autoclass:: configurator.node.ConfigNode
   :members:
   :member-order: bysource
   :special-members:
   :exclude-members: __init__

.. autoclass:: configurator.parsers.ParseError


Mapping and Merging
-------------------

.. attribute:: configurator.source

    The root generative source :class:`~configurator.path.Path` for
    creating :doc:`mappings <mapping>`.

.. attribute:: configurator.target

    The root generative target :class:`~configurator.path.Path` for
    creating :doc:`mappings <mapping>`.

.. autofunction:: configurator.convert

.. autofunction:: configurator.required

.. autofunction:: configurator.if_supplied

.. autofunction:: configurator.value

.. autoclass:: configurator.path.Path
   :members:
   :member-order: bysource
   :special-members:
   :exclude-members: __weakref__, __str__, __repr__, __init__

.. attribute:: configurator.default_mergers

    The default set of mergers, which recursively merge :class:`dicts <dict>`
    using the union of their keys and merge :class:`lists <list>` by appending
    the contents of the new list to the existing list.


Patterns of use
---------------

.. automodule:: configurator.patterns
   :members:
