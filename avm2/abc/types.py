from __future__ import annotations

import math
from dataclasses import dataclass
from functools import partial
from typing import Optional, Tuple

from avm2.abc.enums import MultinameKind, NamespaceKind, MethodFlags, OptionKind
from avm2.abc.parser import read_array, read_array_with_default, read_string
from avm2.io import MemoryViewReader


@dataclass
class ABCFile:
    minor_version: int
    major_version: int
    constant_pool: ConstantPool
    methods: Tuple[MethodInfo, ...]

    def __init__(self, raw: memoryview):
        reader = MemoryViewReader(raw)
        self.minor_version = reader.read_u16()
        self.major_version = reader.read_u16()
        self.constant_pool = ConstantPool(reader)
        self.methods = read_array(reader, MethodInfo)


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
    return_type: int
    param_types: Tuple[int, ...]
    name: int
    flags: MethodFlags
    options: Optional[Tuple[OptionDetail, ...]] = None
    param_names: Optional[Tuple[int, ...]] = None

    def __init__(self, reader: MemoryViewReader):
        self.param_count = reader.read_int()
        self.return_type = reader.read_int()
        self.param_types = read_array(reader, MemoryViewReader.read_int, self.param_count)
        self.name = reader.read_int()
        self.flags = MethodFlags(reader.read_u8())
        if MethodFlags.HAS_OPTIONAL in self.flags:
            self.options = read_array(reader, OptionDetail)
        if MethodFlags.HAS_PARAM_NAMES in self.flags:
            self.param_names = read_array(reader, MemoryViewReader.read_int, self.param_count)


@dataclass
class OptionDetail:
    val: int
    kind: OptionKind

    def __init__(self, reader: MemoryViewReader):
        self.val = reader.read_int()
        self.kind = OptionKind(reader.read_u8())
