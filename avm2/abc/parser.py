import math
from functools import partial
from typing import Callable, Tuple, TypeVar, Optional

from avm2.abc.types import *
from avm2.io import MemoryViewReader

T = TypeVar('T')


def parse_abc_file(raw: memoryview) -> ABCFile:
    """
    Parse abcFile structure.
    """
    reader = MemoryViewReader(raw)
    return ABCFile(
        minor_version=reader.read_u16(),
        major_version=reader.read_u16(),
        constant_pool=read_constant_pool(reader),
    )


def read_array(reader: MemoryViewReader, read: Callable[[MemoryViewReader], T], default: Optional[T]) -> Tuple[T, ...]:
    return (default,) + tuple(read(reader) for _ in range(reader.read_int() - 1))


def read_constant_pool(reader: MemoryViewReader) -> ConstantPool:
    return ConstantPool(
        integers=read_array(reader, partial(MemoryViewReader.read_int, unsigned=False), 0),
        unsigned_integers=read_array(reader, MemoryViewReader.read_int, 0),
        doubles=read_array(reader, MemoryViewReader.read_d64, math.nan),
        strings=read_array(reader, read_string, None),
        namespaces=read_array(reader, read_namespace, None),
        ns_sets=read_array(reader, read_namespace_set, None),
        multinames=read_array(reader, read_multiname, None),
    )


def read_string(reader: MemoryViewReader) -> str:
    return reader.read(reader.read_int()).tobytes().decode('utf-8')


def read_namespace(reader: MemoryViewReader) -> Namespace:
    return Namespace(kind=NamespaceKind(reader.read_u8()), name=reader.read_int())


def read_namespace_set(reader: MemoryViewReader) -> NamespaceSet:
    return NamespaceSet(namespaces=tuple(reader.read_int() for _ in range(reader.read_int())))


def read_multiname(reader: MemoryViewReader) -> Multiname:
    kind = MultinameKind(reader.read_u8())
    if kind in (MultinameKind.Q_NAME, MultinameKind.Q_NAME_A):
        return Multiname(kind=kind, ns=reader.read_int(), name=reader.read_int())
    if kind in (MultinameKind.RTQ_NAME, MultinameKind.RTQ_NAME_A):
        return Multiname(kind=kind, name=reader.read_int())
    if kind in (MultinameKind.RTQ_NAME_L, MultinameKind.RTQ_NAME_LA):
        return Multiname(kind=kind)
    if kind in (MultinameKind.MULTINAME, MultinameKind.MULTINAME_A):
        return Multiname(kind=kind, name=reader.read_int(), ns=reader.read_int())
    if kind in (MultinameKind.MULTINAME_L, MultinameKind.MULTINAME_LA):
        return Multiname(kind=kind, ns=reader.read_int())
    if kind == MultinameKind.TYPE_NAME:
        return Multiname(
            kind=kind,
            q_name=reader.read_int(),
            types=tuple(reader.read_int() for _ in range(reader.read_int())),
        )
    assert False, 'unreachable code'
