import os
from copy import deepcopy
from io import open, StringIO
from os.path import exists, expanduser

from .mapping import load, store, target, convert, if_supplied
from .merge import MergeContext
from .node import ConfigNode
from .parsers import Parsers
from .path import parse_text


class Config(ConfigNode):
    """
    The root of the configuration store.
    """

    __slots__ = ConfigNode.__slots__+('_previous',)

    parsers = Parsers()

    def __init__(self, data=None):
        super(Config, self).__init__(data)
        self._previous = []

    @classmethod
    def from_text(cls, text, parser, encoding='ascii'):
        """
        Construct a :class:`Config` from the provided ``text`` using the specified
        :doc:`parser <parsers>`. If ``text`` is provided as :class:`bytes`, then
        the ``encoding`` specified will be used to decode it.
        """
        if isinstance(text, bytes):
            text = text.decode(encoding)
        return cls.from_stream(StringIO(text), parser)

    @classmethod
    def from_stream(cls, stream, parser=None):
        """
        Construct a :class:`Config` from a stream such as a :func:`file <open>`.
        If the stream does not have a ``name`` attribute from which the correct
        parser can be guessed, :doc:`parser <parsers>` must be specified.
        If ``text`` is provided as :class:`bytes`, then the ``encoding``
        specified will be used to decode it.
        """
        if parser is None:
            name = getattr(stream, 'name', None)
            if name is not None:
                try:
                    _, parser = name.rsplit('.', 1)
                except ValueError:
                    pass
        if not callable(parser):
            parser = cls.parsers[parser]
        return cls(parser(stream))

    @classmethod
    def from_path(cls, path, parser=None, encoding=None, optional=False):
        """
        Construct a :class:`Config` from file specified as a path. This path
        with have ``~`` expanded. If specified, ``encoding`` will be used to
        decode the content of the file. An explicit :doc:`parser <parsers>`
        can be specified, if necessary, but the correct one will usually be
        guessed from the file extension.

        If ``optional`` is ``True``, then an empty :class:`Config` will be
        returned if the file does not exist.
        """
        full_path = expanduser(path)
        if optional and not exists(full_path):
            return cls()
        with open(full_path, encoding=encoding) as stream:
            return cls.from_stream(stream, parser)

    @classmethod
    def from_env(cls, prefix, types=None):
        """
        Construct a :class:`Config` from :data:`os.environ` entries
        that matches the specified ``prefix``.
        ``prefix`` can either be a simple string prefix
        or a :class:`dict` mapping string prefixes to the
        :doc:`target paths <mapping>` at which they will be stored.
        ``types`` is an optional :class:`dict` mapping string suffixes
        to callables used to convert matching environment values to the
        correct type.
        """
        if not isinstance(prefix, dict):
            prefixes = {prefix: target}
        else:
            prefixes = prefix
        mapping = {}
        for key, value in os.environ.items():
            for prefix, prefix_target in prefixes.items():
                if key.startswith(prefix):
                    prefix_source = if_supplied(key)
                    prefix_target = parse_text(prefix_target)[key[len(prefix):].lower()]
                    if types is not None:
                        for suffix, type_ in types.items():
                            if key.endswith(suffix):
                                prefix_source = convert(prefix_source, type_)
                    mapping[prefix_source] = prefix_target

        config = cls()
        config.merge(os.environ, mapping)
        return config

    def merge(self, source=None, mapping=None, mergers=None):
        """
        Modify this :class:`Config` by merging the provided ``source`` into
        it using any ``mapping`` or ``mergers`` provided.

        See :doc:`mapping` for more detail.
        """
        if isinstance(source, Config):
            source = source.data
        context = MergeContext(mergers)
        if mapping is None:
            self.data = context.merge(source, self.data)
        else:
            for source_path, target_path in mapping.items():
                value = load(source, source_path)
                self.data = store(self.data, target_path, value, context)

    def clone(self):
        """
        Clone this :class:`Config` creating copies of all mutable objects
        it contains.
        """
        return Config(deepcopy(self.data))

    def __add__(self, other):
        """
        Configuration stores can be added together.
        This will result in a new :class:`Config` object being returned that
        is created by merging the two original configs.
        """
        result = self.clone()
        result.merge(other)
        return result

    def push(self, config=None, empty=False):
        """
        Push the provided ``config`` onto this instance, replacing the data
        of this :class:`Config`.

        If ``empty`` is ``False``, this is done by merging the existing
        contents with the provided ``config``, giving precedence to the
        ``config`` passed in.

        If ``empty`` is ``True``, then the provided ``config`` is used to
        entirely replace the data of this :class:`Config`.

        ``config`` may either be a :class:`Config` instance or anything
        that would be passed to the :class:`Config` constructor.

        This method returns a context manager that, when its context is left,
        restores the configuration data used to whatever was in place
        before :meth:`push` was called, regardless of any further :meth:`push`
        or meth:`merge` calls, or other modifications to :attr:`data` on this
        :class:`Config` object.
        """
        if empty:
            base = Config()
        else:
            base = self.clone()
        if not isinstance(config, Config):
            config = Config(config)
        self._previous.append(self.data)
        context = PushContext(self, self.data)
        self.data = (base + config).data
        return context

    def pop(self):
        """
        Pop off the top-most data that was last :meth:`pushed <push>`
        on to this :class:`Config`.
        """
        self.data = self._previous.pop()


class PushContext(object):

    def __init__(self, config, data):
        self.config = config
        self.data = data

    def __enter__(self):
        return self.config

    def __exit__(self, exc_type, exc_val, exc_tb):
        while self.config.data is not self.data:
            self.config.pop()
