import pytest
from testfixtures import compare

from configurator import Config


def test_load_toml_from_path_implicit_parser(tmp_path):
    path = tmp_path / 'test.toml'
    path.write_bytes(b'k = "v"')
    config = Config.from_path(path)
    compare(config.k, "v")


def test_load_toml_from_path_explicit_parser(tmp_path):
    path = tmp_path / 'test.toml'
    path.write_bytes(b'k = "v"')
    parser = Config.parsers['toml']
    config = Config.from_path(path, parser)
    compare(config.k, "v")


def test_load_toml_from_byte_stream_implicit_parser(tmp_path):
    path = tmp_path / 'test.toml'
    path.write_bytes(b'k = "v"')
    with path.open(mode="rb") as stream:
        config = Config.from_stream(stream)
    compare(config.k, "v")


def test_load_toml_from_byte_stream_explicit_parser(tmp_path):
    path = tmp_path / 'test.toml'
    path.write_bytes(b'k = "v"')
    parser = Config.parsers['toml']
    with path.open(mode="rb") as stream:
        config = Config.from_stream(stream, parser)
    compare(config.k, "v")


def test_load_toml_from_text_stream_implicit_parser(tmp_path):
    path = tmp_path / 'test.toml'
    path.write_bytes(b'k = "v"')
    with path.open(mode="rt") as stream:
        config = Config.from_stream(stream)
    compare(config.k, "v")


def test_load_toml_from_text_stream_explicit_parser(tmp_path):
    path = tmp_path / 'test.toml'
    path.write_bytes(b'k = "v"')
    parser = Config.parsers['toml']
    with path.open(mode="rt") as stream:
        config = Config.from_stream(stream, parser)
    compare(config.k, "v")


def test_load_toml_from_text():
    parser = Config.parsers['toml']
    config = Config.from_text('k = "v"', parser)
    compare(config.k, "v")


def test_load_toml_from_bytes():
    parser = Config.parsers['toml']
    config = Config.from_text(b'k = "v"', parser)
    compare(config.k, "v")
