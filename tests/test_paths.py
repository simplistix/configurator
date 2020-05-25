from testfixtures import compare

from configurator.mapping import source, target, required, convert, value
from configurator.path import parse_text


class TestPaths(object):

    def test_repr(self):
        compare(repr(source), expected="Path:source")
        compare(repr(target), expected="Path:target")

    def test_str(self):
        compare(str(source), expected="source")
        compare(str(target), expected="target")

    def test_repr_nested(self):
        compare(repr(
            required(convert(source['foo'].y, int)).insert(0).append().merge()
        ), expected=(
            "Path:required(convert(source['foo'].y, int)).insert(0).append().merge()"
        ))

    def test_str_nested(self):
        compare(str(
            required(convert(source['foo'].y, int)).insert(0).append().merge()
        ), expected=(
            "required(convert(source['foo'].y, int)).insert(0).append().merge()"
        ))

    def test_repr_value(self):
        compare(str(value(42)), expected="value(42)")

    def test_text_op(self):
        compare(str(parse_text('x.y.z')), expected='x.y.z')

    def test_convert_no_name(self):
        o = object()
        compare(str(convert(source, o)), expected=(
            "convert(source, {!r})".format(o)
        ))
