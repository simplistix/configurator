from configurator.proxy import Proxy
from testfixtures import ShouldRaise, compare
from testfixtures.mock import Mock


def test_unnamed_unconfigured():
    proxy = Proxy()
    with ShouldRaise(RuntimeError('Cannot use proxy before it is configured')):
        proxy.foo


def test_named_unconfigured():
    proxy = Proxy('My Foo')
    with ShouldRaise(RuntimeError('Cannot use My Foo before it is configured')):
        proxy.foo


def test_configured_attr():
    proxy = Proxy()
    foo = Mock()
    proxy.set(foo)
    assert proxy.bar is foo.bar


def test_configured_function():

    def foo(n):
        return n+1

    proxy = Proxy()
    proxy.set(foo)

    compare(proxy(1), expected=2)


def test_clone():
    proxy = Proxy('foo')
    proxy.set(1)
    proxy_ = proxy.clone()
    proxy_.set(2)
    compare(proxy.get(), expected=1)
    compare(proxy_.get(), expected=2)
    compare(proxy_._name, expected='foo')
