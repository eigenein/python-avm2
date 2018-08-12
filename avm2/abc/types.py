from __future__ import annotations

import math
from dataclasses import dataclass
from functools import partial
from typing import Optional, Tuple, Union

from avm2.abc.enums import (
    ClassFlags,
    ConstantKind,
    MethodFlags,
    MultinameKind,
    NamespaceKind,
    TraitAttributes,
    TraitKind,
)
from avm2.abc.parser import read_array, read_array_with_default, read_string
from avm2.io import MemoryViewReader


@dataclass
class ABCFile:
    minor_version: int
    major_version: int
    constant_pool: ConstantPool
    methods: Tuple[MethodInfo, ...]
    metadata: Tuple[MetadataInfo, ...]
    instances: Tuple[InstanceInfo, ...]
    classes: Tuple[ClassInfo, ...]
    scripts: Tuple[ScriptInfo, ...]
    method_bodies: Tuple[MethodBodyInfo, ...]

    def __init__(self, reader: MemoryViewReader):
        self.minor_version = reader.read_u16()
        self.major_version = reader.read_u16()
        self.constant_pool = ConstantPool(reader)
        self.methods = read_array(reader, MethodInfo)
        self.metadata = read_array(reader, MetadataInfo)
        class_count = reader.read_int()
        self.instances = read_array(reader, InstanceInfo, class_count)
        self.classes = read_array(reader, ClassInfo, class_count)
        self.scripts = read_array(reader, ScriptInfo)
        self.method_bodies = read_array(reader, MethodBodyInfo)


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
    kind: ConstantKind

    def __init__(self, reader: MemoryViewReader):
        self.val = reader.read_int()
        self.kind = ConstantKind(reader.read_u8())


@dataclass
class MetadataInfo:
    name: int
    items: Tuple[ItemInfo, ...]

    def __init__(self, reader: MemoryViewReader):
        self.name = reader.read_int()
        self.items = read_array(reader, ItemInfo)


@dataclass
class ItemInfo:
    key: int
    value: int

    def __init__(self, reader: MemoryViewReader):
        self.key = reader.read_int()
        self.value = reader.read_int()


@dataclass
class InstanceInfo:
    name: int
    super_name: int
    flags: ClassFlags
    interfaces: Tuple[int, ...]
    init_instance: int
    traits: Tuple[TraitInfo, ...]
    protected_ns: Optional[int] = None

    def __init__(self, reader: MemoryViewReader):
        self.name = reader.read_int()
        self.super_name = reader.read_int()
        self.flags = ClassFlags(reader.read_u8())
        if ClassFlags.PROTECTED_NS in self.flags:
            self.protected_ns = reader.read_int()
        self.interfaces = read_array(reader, MemoryViewReader.read_int)
        self.init_instance = reader.read_int()
        self.traits = read_array(reader, TraitInfo)


@dataclass
class TraitInfo:
    name: int
    kind: TraitKind
    attributes: TraitAttributes
    data: Union[TraitSlot, TraitClass, TraitFunction, TraitMethod]
    metadata: Optional[Tuple[int, ...]] = None

    def __init__(self, reader: MemoryViewReader):
        self.name = reader.read_int()
        kind = reader.read_u8()
        self.kind = TraitKind(kind & 0x0F)
        self.attributes = TraitAttributes(kind >> 4)
        if self.kind in (TraitKind.SLOT, TraitKind.CONST):
            self.data = TraitSlot(reader)
        elif self.kind == TraitKind.CLASS:
            self.data = TraitClass(reader)
        elif self.kind == TraitKind.FUNCTION:
            self.data = TraitFunction(reader)
        elif self.kind in (TraitKind.METHOD, TraitKind.GETTER, TraitKind.SETTER):
            self.data = TraitMethod(reader)
        else:
            assert False, 'unreachable code'
        if TraitAttributes.METADATA in self.attributes:
            self.metadata = read_array(reader, MemoryViewReader.read_int)


@dataclass
class TraitSlot:
    slot_id: int
    type_name: int
    vindex: int
    vkind: ConstantKind

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.type_name = reader.read_int()
        self.vindex = reader.read_int()
        if self.vindex:
            self.vkind = ConstantKind(reader.read_u8())


@dataclass
class TraitClass:
    slot_id: int
    class_: int

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.class_ = reader.read_int()


@dataclass
class TraitFunction:
    slot_id: int
    function_: int

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.function_ = reader.read_int()


@dataclass
class TraitMethod:
    disposition_id: int
    method: int

    def __init__(self, reader: MemoryViewReader):
        self.disposition_id = reader.read_int()
        self.method = reader.read_int()


@dataclass
class ClassInfo:
    init_class: int
    traits: Tuple[TraitInfo, ...]

    def __init__(self, reader: MemoryViewReader):
        self.init_class = reader.read_int()
        self.traits = read_array(reader, TraitInfo)


@dataclass
class ScriptInfo:
    init: int
    traits: Tuple[TraitInfo, ...]

    def __init__(self, reader: MemoryViewReader):
        self.init = reader.read_int()
        self.traits = read_array(reader, TraitInfo)


@dataclass
class MethodBodyInfo:
    method: int
    max_stack: int
    local_count: int
    init_scope_depth: int
    max_scope_depth: int
    code: memoryview
    exceptions: Tuple[ExceptionInfo, ...]
    traits: Tuple[TraitInfo, ...]

    def __init__(self, reader: MemoryViewReader):
        self.method = reader.read_int()
        self.max_stack = reader.read_int()
        self.local_count = reader.read_int()
        self.init_scope_depth = reader.read_int()
        self.max_scope_depth = reader.read_int()
        self.code = reader.read(reader.read_int())
        self.exceptions = read_array(reader, ExceptionInfo)
        self.traits = read_array(reader, TraitInfo)


@dataclass
class ExceptionInfo:
    from_: int
    to: int
    target: int
    exc_type: int
    var_name: int

    def __init__(self, reader: MemoryViewReader):
        self.from_ = reader.read_int()
        self.to = reader.read_int()
        self.target = reader.read_int()
        self.exc_type = reader.read_int()
        self.var_name = reader.read_int()
