from pprint import pformat


class ConfigNode(object):
    """
    A node in the configuration store.
    These are obtained by using the methods below on :class:`~configurator.Config`
    objects or any :class:`ConfigNode` objects returned by them.
    """

    __slots__ = ('data',)

    def __init__(self, data=None):
        if data is None:
            data = {}
        #: The underlying python object for this node, often a :class:`dict`
        #: or a :class:`list`. While this is part of the public API, care should
        #: be taken when using it, particularly if you choose to modify it.
        self.data = data

    @classmethod
    def _wrap(cls, value):
        if isinstance(value, (dict, list)):
            value = ConfigNode(value)
        return value

    def _get(self, name):
        try:
            value = self.data[name]
        except TypeError:
            raise KeyError(name)
        return self._wrap(value)

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

    def __getitem__(self, name):
        """
        Obtain a child of this node by item access. If the child
        is a :class:`dict` or :class:`list`, a :class:`ConfigNode` for it will
        be returned, otherwise the value itself will be returned.
        """
        return self._get(name)

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
            yield key, self._wrap(value)

    def __iter__(self):
        """
        Obtain children of this node by either :class:`dict` or :class:`list`
        iteration, depending on the type of the underlying :attr:`data`.
        If the child is a :class:`dict` or :class:`list`, a :class:`ConfigNode`
        for it will be returned, otherwise the value itself will be returned.
        """
        for item in self.data:
            yield self._wrap(item)

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
