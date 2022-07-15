class Proxy:
    """
    A proxy is an object that can be passed around to present another object
    that needs to be referenced during configuration parsing but cannot be used
    until configuration parsing is completed.
    """

    _object = None

    def __init__(self, name='proxy'):
        self._name = name

    def __deepcopy__(self, memo):
        # Merging and cloning make use of deepcopy. Proxies should not be
        # copied as part of this process, so this is disabled here:
        return self

    def set(self, obj):
        self._object = obj

    def get(self):
        if self._object is None:
            raise RuntimeError(f'Cannot use {self._name} before it is configured')
        return self._object

    def clone(self):
        proxy = type(self)(self._name)
        proxy.set(self._object)
        return proxy

    def __getattr__(self, item):
        return getattr(self.get(), item)

    def __call__(self, *args, **kw):
        return self.__getattr__('__call__')(*args, **kw)
