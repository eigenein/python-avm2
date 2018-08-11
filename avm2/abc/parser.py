from __future__ import annotations

from typing import Callable, Optional, Tuple, TypeVar

from avm2.io import MemoryViewReader

T = TypeVar('T')


def read_string(reader: MemoryViewReader) -> str:
    return reader.read(reader.read_int()).tobytes().decode('utf-8')


def read_array(reader: MemoryViewReader, read: Callable[[MemoryViewReader], T], size: Optional[int] = None) -> Tuple[T, ...]:
    """
    Read variable-length array.
    """
    if size is None:
        size = reader.read_int()
    return tuple(read(reader) for _ in range(size))


def read_array_with_default(reader: MemoryViewReader, read: Callable[[MemoryViewReader], T], default: Optional[T]) -> Tuple[T, ...]:
    """
    Read variable-length array where 0-th element has a "special meaning".
    """
    return (default, *(read(reader) for _ in range(1, reader.read_int())))
