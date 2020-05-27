from pprint import pformat

from .path import parse_text, NotPresent


class ConfigNode(object):
    """
    A node in the configuration store.
    These are obtained by using the methods below on :class:`~configurator.Config`
    objects or any :class:`ConfigNode` objects returned by them.
    """

    __slots__ = ('_container', '_accessor', 'data')

    def __init__(self, data=None, container=None, accessor=None):
        if data is None:
            data = {}
        #: The underlying python object for this node, often a :class:`dict`
        #: or a :class:`list`. While this is part of the public API, care should
        #: be taken when using it, particularly if you choose to modify it.
        self.data = data
        self._container = container
        self._accessor = accessor

    def _wrap(self, accessor, value):
        if isinstance(value, (dict, list)):
            value = ConfigNode(value, self.data, accessor)
        return value

    def _get(self, name):
        try:
            value = self.data[name]
        except TypeError:
            raise KeyError(name)
        return self._wrap(name, value)

    def __getattr__(self, name):
        """
        Obtain a child of this node by attribute access. If the child
        is a :class:`dict` or :class:`list`, a :class:`ConfigNode` for it will
        be returned, otherwise the value itself will be returned.
        """
        try:
            return self._get(name)
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """
        Set a child of this node. This is a convenience helper that
        calls :meth:`__setitem__` and can be used when ``name`` is a string.
        """
        if name in self.__slots__:
            super(ConfigNode, self).__setattr__(name, value)
        else:
            self[name] = value

    def __getitem__(self, name):
        """
        Obtain a child of this node by item access. If the child
        is a :class:`dict` or :class:`list`, a :class:`ConfigNode` for it will
        be returned, otherwise the value itself will be returned.
        """
        return self._get(name)

    def __setitem__(self, name, value):
        """
        Set the ``value`` for the supplied ``name`` in :attr:`data`.
        If :attr:`data` is a :class:`dict`, then ``name`` must be a :class:`str`.
        If :attr:`data` is a :class:`list`, then ``name`` must be an :class:`int`.
        """
        self.data[name] = value

    def get(self, name, default=None):
        """
        Obtain a child of this node by access like :meth:`dict.get`. If the child
        is a :class:`dict` or :class:`list`, a :class:`ConfigNode` for it will
        be returned, otherwise the value itself will be returned.
        """
        try:
            return self._get(name)
        except KeyError:
            return default

    def items(self):
        """
        Obtain children of this node by access like :meth:`dict.items`. If the child
        is a :class:`dict` or :class:`list`, a :class:`ConfigNode` for it will
        be returned, otherwise the value itself will be returned.
        """
        for key, value in sorted(self.data.items()):
            yield key, self._wrap(key, value)

    def __iter__(self):
        """
        Obtain children of this node by either :class:`dict` or :class:`list`
        iteration, depending on the type of the underlying :attr:`data`.
        If the child is a :class:`dict` or :class:`list`, a :class:`ConfigNode`
        for it will be returned, otherwise the value itself will be returned.
        """
        for index, item in enumerate(self.data):
            yield self._wrap(index, item)

    def node(self, path=None, create=False):
        """
        Obtain a child of this node using a dotted path or
        :class:`~configurator.path.Path` such as one generated from
        :attr:`~configurator.source`. ``path`` may also be a simple string or integer, in
        which case it will be used to obtain a child of this node using item access.

        This always returns a :class:`ConfigNode` or raises an exception if the path
        cannot be resolved. This allows you to use :meth:`set` even for values in dictionaries
        or items in lists.

        If ``create`` is ``True``, all nodes along the path will be created as dictionaries
        if they do not exist.
        """
        if path is None:
            return self

        path = parse_text(path)
        if not path.ops:
            return self

        if create:
            action = 'ensure'
        else:
            action = 'get'

        data = self.data
        for op in path.ops:
            if isinstance(data, NotPresent):
                op.not_present(data)
            else:
                container = data
                data = getattr(op, action)(container)

        if isinstance(data, NotPresent):
            raise data

        text = getattr(op, 'text', None)
        if text is None:
            raise TypeError('invalid path: '+str(path))

        return ConfigNode(data, container, op.text)

    def set(self, value):
        """
        Replace the :attr:`data` of this node with the supplied ``value``.
        """
        if self._container is None:
            self.data = value
        else:
            self._container[self._accessor] = value

    def __repr__(self):
        cls = type(self)
        pretty = pformat(self.data, width=70)
        if '\n' in pretty:
            pretty = '\n'+pretty+'\n'
        return '{}.{}({})'.format(
            cls.__module__,
            cls.__name__,
            pretty
        )

    def __getstate__(self):
        return {name: getattr(self, name) for name in self.__slots__}

    def __setstate__(self, data):
        for name, value in data.items():
            setattr(self, name, value)
