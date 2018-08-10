from __future__ import annotations

from enum import IntEnum
from typing import NamedTuple, Tuple, Optional


class NamespaceKind(IntEnum):
    NAMESPACE = 0x08
    PACKAGE_NAMESPACE = 0x16
    PACKAGE_INTERNAL_NS = 0x17
    PROTECTED_NAMESPACE = 0x18
    EXPLICIT_NAMESPACE = 0x19
    STATIC_PROTECTED_NS = 0x1A
    PRIVATE_NS = 0x05


class MultinameKind(IntEnum):
    Q_NAME = 0x07
    Q_NAME_A = 0x0D
    RTQ_NAME = 0x0F
    RTQ_NAME_A = 0x10
    RTQ_NAME_L = 0x11
    RTQ_NAME_LA = 0x12
    MULTINAME = 0x09
    MULTINAME_A = 0x0E
    MULTINAME_L = 0x1B
    MULTINAME_LA = 0x1C
    TYPE_NAME = 0x1D


class ABCFile(NamedTuple):
    minor_version: int
    major_version: int
    constant_pool: ConstantPool


class ConstantPool(NamedTuple):
    integers: Tuple[int, ...]
    unsigned_integers: Tuple[int, ...]
    doubles: Tuple[float, ...]
    strings: Tuple[str, ...]
    namespaces: Tuple[Namespace, ...]
    ns_sets: Tuple[NamespaceSet, ...]
    multinames: Tuple[Multiname, ...]


class Namespace(NamedTuple):
    kind: NamespaceKind
    name: int


class NamespaceSet(NamedTuple):
    namespaces: Tuple[int, ...]


class Multiname(NamedTuple):
    kind: MultinameKind
    ns: Optional[int] = None
    name: Optional[int] = None
    ns_set: Optional[int] = None
    q_name: Optional[int] = None
    types: Optional[Tuple[int, ...]] = None
