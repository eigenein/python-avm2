from avm2.io import MemoryViewReader


def test_memory_view_reader_read():
    reader = MemoryViewReader(memoryview(b'abc'))
    assert reader.read(1) == b'a'
    assert reader.read(2) == b'bc'
    assert reader.read(1) == b''


def test_memory_view_reader_skip():
    reader = MemoryViewReader(memoryview(b'abc'))
    assert reader.skip(1) == 1


def test_memory_view_reader_read_all():
    reader = MemoryViewReader(memoryview(b'abc'))
    reader.skip(1)
    assert reader.read_all() == b'bc'
    assert reader.read_all() == b''


def test_memory_view_reader_read_u8():
    reader = MemoryViewReader(memoryview(b'\x0A'))
    assert reader.read_u8() == 0x0A


def test_memory_view_reader_read_u16():
    reader = MemoryViewReader(memoryview(b'WS'))
    assert reader.read_u16() == 0x5357


def test_memory_view_reader_read_u32():
    reader = MemoryViewReader(memoryview(b'\x0D\x0C\x0B\x0A'))
    assert reader.read_u32() == 0x0A0B0C0D


def test_memory_view_reader_read_until():
    reader = MemoryViewReader(memoryview(b'ABCDE'))
    reader.skip(1)
    assert reader.read_until(ord('D')) == b'BC'
    assert reader.position == 4


def test_memory_view_reader_read_string():
    reader = MemoryViewReader(memoryview(b'AB\x00CD'))
    assert reader.read_string() == 'AB'
