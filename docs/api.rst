API Reference
=============

.. automodule:: configurator
   :members:
   :member-order: bysource
   :show-inheritance:
   :special-members:
   :exclude-members: __weakref__, __init__

.. attribute:: source

    The root generative source :class:`Path` for creating :doc:`mappings <mapping>`.

.. attribute:: target

    The root generative target :class:`Path` for creating :doc:`mappings <mapping>`.

.. attribute:: default_mergers

    The default set of mergers, which recursively merge :class:`dicts <dict>`
    using the union of their keys and merge :class:`lists <list>` by appending
    the contents of the new list to the existing list.

.. autoclass:: configurator.node.ConfigNode
   :members:
   :member-order: bysource
   :special-members:
   :exclude-members: __init__

.. autoclass:: configurator.path.Path
   :members:
   :member-order: bysource
   :special-members:
   :exclude-members: __weakref__, __str__, __repr__, __init__

.. autoclass:: configurator.parsers.ParseError
