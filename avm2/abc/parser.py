from avm2.abc.types import ABCFile
from avm2.io import MemoryViewReader


def parse_abc_file(raw: memoryview) -> ABCFile:
    """
    Parse abcFile structure.
    """
    reader = MemoryViewReader(raw)
    return ABCFile(
        minor_version=reader.read_u16(),
        major_version=reader.read_u16(),
        # TODO
    )
