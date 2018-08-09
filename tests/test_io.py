from avm2.io import MemoryViewIO


def test_memory_view_io():
    io = MemoryViewIO(memoryview(b'abZcd'))
    assert io.read(1) == b'a'
    assert io.read(1) == b'b'
    assert io.skip(1) == 3
    assert io.read_all() == b'cd'
    assert io.read_all() == b''
