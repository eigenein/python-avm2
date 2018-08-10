from __future__ import annotations

import math
from dataclasses import dataclass
from functools import partial
from typing import Callable, Optional, Tuple, TypeVar

from avm2.abc.enums import MultinameKind, NamespaceKind
from avm2.io import MemoryViewReader

T = TypeVar('T')


def read_string(reader: MemoryViewReader) -> str:
    return reader.read(reader.read_int()).tobytes().decode('utf-8')


def read_array(reader: MemoryViewReader, read: Callable[[MemoryViewReader], T]) -> Tuple[T, ...]:
    """
    Read variable-length array.
    """
    return tuple(read(reader) for _ in range(reader.read_int()))


def read_array_with_default(reader: MemoryViewReader, read: Callable[[MemoryViewReader], T], default: Optional[T]) -> Tuple[T, ...]:
    """
    Read variable-length array where 0-th element has a "special meaning".
    """
    return (default, *(read(reader) for _ in range(1, reader.read_int())))


# TODO: move dataclasses to types.py.

@dataclass
class ABCFile:
    minor_version: int
    major_version: int
    constant_pool: ConstantPool
    # methods: Tuple[MethodInfo, ...]

    def __init__(self, raw: memoryview):
        reader = MemoryViewReader(raw)
        self.minor_version = reader.read_u16()
        self.major_version = reader.read_u16()
        self.constant_pool = ConstantPool(reader)
        # self.methods = read_array(reader, MethodInfo)


@dataclass
class ConstantPool:
    integers: Tuple[int, ...]
    unsigned_integers: Tuple[int, ...]
    doubles: Tuple[float, ...]
    strings: Tuple[str, ...]
    namespaces: Tuple[Namespace, ...]
    ns_sets: Tuple[NamespaceSet, ...]
    multinames: Tuple[Multiname, ...]

    def __init__(self, reader: MemoryViewReader):
        self.integers = read_array_with_default(reader, partial(MemoryViewReader.read_int, unsigned=False), 0)
        self.unsigned_integers = read_array_with_default(reader, MemoryViewReader.read_int, 0)
        self.doubles = read_array_with_default(reader, MemoryViewReader.read_d64, math.nan)
        self.strings = read_array_with_default(reader, read_string, None)
        self.namespaces = read_array_with_default(reader, Namespace, None)
        self.ns_sets = read_array_with_default(reader, NamespaceSet, None)
        self.multinames = read_array_with_default(reader, Multiname, None)


@dataclass
class Namespace:
    kind: NamespaceKind
    name: int

    def __init__(self, reader: MemoryViewReader):
        self.kind = NamespaceKind(reader.read_u8())
        self.name = reader.read_int()


@dataclass
class NamespaceSet:
    namespaces: Tuple[int, ...]

    def __init__(self, reader: MemoryViewReader):
        self.namespaces = read_array(reader, MemoryViewReader.read_int)


@dataclass
class Multiname:
    kind: MultinameKind
    ns: Optional[int] = None
    name: Optional[int] = None
    ns_set: Optional[int] = None
    q_name: Optional[int] = None
    types: Optional[Tuple[int, ...]] = None

    def __init__(self, reader: MemoryViewReader):
        self.kind = MultinameKind(reader.read_u8())
        if self.kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A):
            self.ns = reader.read_int()
            self.name = reader.read_int()
        elif self.kind in (MultinameKind.RTQ_NAME, MultinameKind.RTQ_NAME_A):
            self.name = reader.read_int()
        elif self.kind in (MultinameKind.RTQ_NAME_L, MultinameKind.RTQ_NAME_LA):
            pass
        elif self.kind in (MultinameKind.MULTINAME, MultinameKind.MULTINAME_A):
            self.name = reader.read_int()
            self.ns = reader.read_int()
        elif self.kind in (MultinameKind.MULTINAME_L, MultinameKind.MULTINAME_LA):
            self.ns = reader.read_int()
        elif self.kind == MultinameKind.TYPE_NAME:
            self.q_name = reader.read_int()
            self.types = read_array(reader, MemoryViewReader.read_int)
        else:
            assert False, 'unreachable code'


@dataclass
class MethodInfo:
    param_count: int
    ...
