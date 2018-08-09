from io import SEEK_CUR

from avm2.io import MemoryViewIO


def test_memory_view_io():
    io = MemoryViewIO(memoryview(b'abZcd'))
    assert io.read(1) == b'a'
    assert io.read(1) == b'b'
    io.seek(1, SEEK_CUR)
    assert io.read() == b'cd'
    assert io.read() == b''
