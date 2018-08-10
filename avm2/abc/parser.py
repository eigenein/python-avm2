import math
from functools import partial
from typing import Callable, Tuple, TypeVar, Optional

from avm2.abc import types
from avm2.io import MemoryViewReader

T = TypeVar('T')


def parse_abc_file(raw: memoryview) -> types.ABCFile:
    """
    Parse abcFile structure.
    """
    reader = MemoryViewReader(raw)
    return types.ABCFile(
        minor_version=reader.read_u16(),
        major_version=reader.read_u16(),
        constant_pool=read_constant_pool(reader),
    )


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


def read_constant_pool(reader: MemoryViewReader) -> types.ConstantPool:
    return types.ConstantPool(
        integers=read_array_with_default(reader, partial(MemoryViewReader.read_int, unsigned=False), 0),
        unsigned_integers=read_array_with_default(reader, MemoryViewReader.read_int, 0),
        doubles=read_array_with_default(reader, MemoryViewReader.read_d64, math.nan),
        strings=read_array_with_default(reader, read_string, None),
        namespaces=read_array_with_default(reader, read_namespace, None),
        ns_sets=read_array_with_default(reader, read_namespace_set, None),
        multinames=read_array_with_default(reader, read_multiname, None),
    )


def read_string(reader: MemoryViewReader) -> str:
    return reader.read(reader.read_int()).tobytes().decode('utf-8')


def read_namespace(reader: MemoryViewReader) -> types.Namespace:
    return types.Namespace(kind=types.NamespaceKind(reader.read_u8()), name=reader.read_int())


def read_namespace_set(reader: MemoryViewReader) -> types.NamespaceSet:
    return types.NamespaceSet(namespaces=read_array(reader, MemoryViewReader.read_int))


def read_multiname(reader: MemoryViewReader) -> types.Multiname:
    kind = types.MultinameKind(reader.read_u8())
    if kind in (types.MultinameKind.Q_NAME, types.MultinameKind.Q_NAME_A):
        return types.Multiname(kind=kind, ns=reader.read_int(), name=reader.read_int())
    if kind in (types.MultinameKind.RTQ_NAME, types.MultinameKind.RTQ_NAME_A):
        return types.Multiname(kind=kind, name=reader.read_int())
    if kind in (types.MultinameKind.RTQ_NAME_L, types.MultinameKind.RTQ_NAME_LA):
        return types.Multiname(kind=kind)
    if kind in (types.MultinameKind.MULTINAME, types.MultinameKind.MULTINAME_A):
        return types.Multiname(kind=kind, name=reader.read_int(), ns=reader.read_int())
    if kind in (types.MultinameKind.MULTINAME_L, types.MultinameKind.MULTINAME_LA):
        return types.Multiname(kind=kind, ns=reader.read_int())
    if kind == types.MultinameKind.TYPE_NAME:
        return types.Multiname(kind=kind, q_name=reader.read_int(), types=read_array(reader, MemoryViewReader.read_int))
    assert False, 'unreachable code'
