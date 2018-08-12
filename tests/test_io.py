import pytest

from avm2.io import MemoryViewReader


def test_memory_view_reader_read():
    reader = MemoryViewReader(memoryview(b'abc'))
    assert reader.read(1) == b'a'
    assert reader.read(2) == b'bc'
    assert reader.read(1) == b''


def test_memory_view_reader_skip():
    assert MemoryViewReader(memoryview(b'abc')).skip(1) == 1


def test_memory_view_reader_read_all():
    reader = MemoryViewReader(memoryview(b'abc'))
    reader.skip(1)
    assert reader.read_all() == b'bc'
    assert reader.read_all() == b''


def test_memory_view_reader_read_u8():
    assert MemoryViewReader(memoryview(b'\x0A')).read_u8() == 0x0A


def test_memory_view_reader_read_u16():
    assert MemoryViewReader(memoryview(b'WS')).read_u16() == 0x5357


def test_memory_view_reader_read_u32():
    assert MemoryViewReader(memoryview(b'\x0D\x0C\x0B\x0A')).read_u32() == 0x0A0B0C0D


@pytest.mark.parametrize('bytes_, expected', [
    (b'\x0C\x0B\x0A', 0x0A0B0C),
    (b'\xFF\xFF\xFF', -1),
])
def test_memory_view_reader_read_s24(bytes_: bytes, expected: int):
    assert MemoryViewReader(memoryview(bytes_)).read_s24() == expected


def test_memory_view_reader_read_until():
    reader = MemoryViewReader(memoryview(b'ABCDE'))
    reader.skip(1)
    assert reader.read_until(ord('D')) == b'BC'
    assert reader.position == 4


def test_memory_view_reader_read_string():
    assert MemoryViewReader(memoryview(b'AB\x00CD')).read_string() == 'AB'


@pytest.mark.parametrize('bytes_, unsigned, value', [
    (b'\x7F', True, 0x7F),
    (b'\xFF\x7F', True, 0x3FFF),
    (b'\xFF\xFF\x7F', True, 0x1FFFFF),
    (b'\xFF\xFF\xFF\x7F', True, 0xFFFFFFF),
    (b'\xFF\xFF\xFF\xFF\x0F', True, 0xFFFFFFFF),
    (b'\xFF\xFF\xFF\xFF\x7F', False, -1),
    (b'\x7F', False, -1),
    (b'\x0F', False, 15),
])
def test_memory_view_reader_read_int(bytes_: bytes, unsigned: bool, value: int):
    assert MemoryViewReader(bytes_).read_int(unsigned) == value


def test_is_eof():
    reader = MemoryViewReader(memoryview(b'ABCDE'))
    assert not reader.is_eof()
    reader.read(4)
    assert not reader.is_eof()
    reader.read(2)
    assert reader.is_eof()
    reader.skip(42)
    assert reader.is_eof()
