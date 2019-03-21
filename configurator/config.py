from io import open, StringIO
from os.path import exists, expanduser
from .node import ConfigNode
from .mapping import load, store
from .merge import MergeContext
from .parsers import Parsers


class Config(ConfigNode):
    """
    The root of the configuration store.
    """

    parsers = Parsers.from_entrypoints()

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
            parser = cls.parsers.get(parser)
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

    def merge(self, source, mapping=None, mergers=None):
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

    def __add__(self, other):
        """
        Configuration stores can be added together.
        This will result in a new :class:`Config` object being returned that
        is created by merging the two original configs.
        """
        result = Config(type(self.data)())
        result.merge(self)
        result.merge(other)
        return result
