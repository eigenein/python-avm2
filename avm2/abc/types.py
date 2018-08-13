from __future__ import annotations

import math
from dataclasses import dataclass
from functools import partial
from typing import Optional, List, Union, NewType

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

ABCStringIndex = NewType('ABCStringIndex', int)
ABCNamespaceIndex = NewType('ABCNamespaceIndex', int)
ABCNamespaceSetIndex = NewType('ABCNamespaceSetIndex', int)
ABCMultinameIndex = NewType('ABCMultinameIndex', int)
ABCMethodIndex = NewType('ABCMethodIndex', int)
ABCMetadataIndex = NewType('ABCMetadataIndex', int)
ABCClassIndex = NewType('ABCClassIndex', int)


@dataclass
class ABCFile:
    minor_version: int
    major_version: int
    constant_pool: ASConstantPool
    methods: List[ASMethod]
    metadata: List[ASMetadata]
    instances: List[ASInstance]
    classes: List[ASClass]
    scripts: List[ASScript]
    method_bodies: List[ASMethodBody]

    def __init__(self, reader: MemoryViewReader):
        self.minor_version = reader.read_u16()
        self.major_version = reader.read_u16()
        self.constant_pool = ASConstantPool(reader)
        self.methods = read_array(reader, ASMethod)
        self.metadata = read_array(reader, ASMetadata)
        class_count = reader.read_int()
        self.instances = read_array(reader, ASInstance, class_count)
        self.classes = read_array(reader, ASClass, class_count)
        self.scripts = read_array(reader, ASScript)
        self.method_bodies = read_array(reader, ASMethodBody)


@dataclass
class ASConstantPool:
    integers: List[int]
    unsigned_integers: List[int]
    doubles: List[float]
    strings: List[str]
    namespaces: List[ASNamespace]
    ns_sets: List[ASNamespaceSet]
    multinames: List[ASMultiname]

    def __init__(self, reader: MemoryViewReader):
        self.integers = read_array_with_default(reader, partial(MemoryViewReader.read_int, unsigned=False), 0)
        self.unsigned_integers = read_array_with_default(reader, MemoryViewReader.read_int, 0)
        self.doubles = read_array_with_default(reader, MemoryViewReader.read_d64, math.nan)
        self.strings = read_array_with_default(reader, read_string, None)
        self.namespaces = read_array_with_default(reader, ASNamespace, None)
        self.ns_sets = read_array_with_default(reader, ASNamespaceSet, None)
        self.multinames = read_array_with_default(reader, ASMultiname, None)


@dataclass
class ASNamespace:
    kind: NamespaceKind
    name: ABCStringIndex

    def __init__(self, reader: MemoryViewReader):
        self.kind = NamespaceKind(reader.read_u8())
        self.name = reader.read_int()


@dataclass
class ASNamespaceSet:
    namespaces: List[ABCNamespaceIndex]

    def __init__(self, reader: MemoryViewReader):
        self.namespaces = read_array(reader, MemoryViewReader.read_int)


@dataclass
class ASMultiname:
    kind: MultinameKind
    ns: Optional[ABCNamespaceIndex] = None
    name: Optional[ABCStringIndex] = None
    ns_set: Optional[ABCNamespaceSetIndex] = None
    q_name: Optional[ABCMultinameIndex] = None
    types: Optional[List[ABCMultinameIndex]] = None

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
class ASMethod:
    param_count: int
    return_type: ABCMultinameIndex
    param_types: List[ABCMultinameIndex]
    name: ABCStringIndex
    flags: MethodFlags
    options: Optional[List[ASOptionDetail]] = None
    param_names: Optional[List[ABCStringIndex]] = None

    def __init__(self, reader: MemoryViewReader):
        self.param_count = reader.read_int()
        self.return_type = reader.read_int()
        self.param_types = read_array(reader, MemoryViewReader.read_int, self.param_count)
        self.name = reader.read_int()
        self.flags = MethodFlags(reader.read_u8())
        if MethodFlags.HAS_OPTIONAL in self.flags:
            self.options = read_array(reader, ASOptionDetail)
        if MethodFlags.HAS_PARAM_NAMES in self.flags:
            self.param_names = read_array(reader, MemoryViewReader.read_int, self.param_count)


@dataclass
class ASOptionDetail:
    value: int
    kind: ConstantKind

    def __init__(self, reader: MemoryViewReader):
        self.value = reader.read_int()
        self.kind = ConstantKind(reader.read_u8())


@dataclass
class ASMetadata:
    name: ABCStringIndex
    items: List[ASItem]

    def __init__(self, reader: MemoryViewReader):
        self.name = reader.read_int()
        self.items = read_array(reader, ASItem)


@dataclass
class ASItem:
    key: ABCStringIndex
    value: ABCStringIndex

    def __init__(self, reader: MemoryViewReader):
        self.key = reader.read_int()
        self.value = reader.read_int()


@dataclass
class ASInstance:
    name: ABCMultinameIndex
    super_name: ABCMultinameIndex
    flags: ClassFlags
    interfaces: List[ABCMultinameIndex]
    init: ABCMethodIndex
    traits: List[ASTrait]
    protected_ns: Optional[ABCNamespaceIndex] = None

    def __init__(self, reader: MemoryViewReader):
        self.name = reader.read_int()
        self.super_name = reader.read_int()
        self.flags = ClassFlags(reader.read_u8())
        if ClassFlags.PROTECTED_NS in self.flags:
            self.protected_ns = reader.read_int()
        self.interfaces = read_array(reader, MemoryViewReader.read_int)
        self.init = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASTrait:
    name: ABCMultinameIndex
    kind: TraitKind
    attributes: TraitAttributes
    data: Union[ASTraitSlot, ASTraitClass, ASTraitFunction, ASTraitMethod]
    metadata: Optional[List[ABCMetadataIndex]] = None

    def __init__(self, reader: MemoryViewReader):
        self.name = reader.read_int()
        kind = reader.read_u8()
        self.kind = TraitKind(kind & 0x0F)
        self.attributes = TraitAttributes(kind >> 4)
        if self.kind in (TraitKind.SLOT, TraitKind.CONST):
            self.data = ASTraitSlot(reader)
        elif self.kind == TraitKind.CLASS:
            self.data = ASTraitClass(reader)
        elif self.kind == TraitKind.FUNCTION:
            self.data = ASTraitFunction(reader)
        elif self.kind in (TraitKind.METHOD, TraitKind.GETTER, TraitKind.SETTER):
            self.data = ASTraitMethod(reader)
        else:
            assert False, 'unreachable code'
        if TraitAttributes.METADATA in self.attributes:
            self.metadata = read_array(reader, MemoryViewReader.read_int)


@dataclass
class ASTraitSlot:
    slot_id: int
    type_name: ABCMultinameIndex
    vindex: int
    vkind: Optional[ConstantKind] = None

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.type_name = reader.read_int()
        self.vindex = reader.read_int()
        if self.vindex:
            self.vkind = ConstantKind(reader.read_u8())


@dataclass
class ASTraitClass:
    slot_id: int
    class_: ABCClassIndex

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.class_ = reader.read_int()


@dataclass
class ASTraitFunction:
    slot_id: int
    function_: ABCMethodIndex

    def __init__(self, reader: MemoryViewReader):
        self.slot_id = reader.read_int()
        self.function_ = reader.read_int()


@dataclass
class ASTraitMethod:
    disposition_id: int
    method: ABCMethodIndex

    def __init__(self, reader: MemoryViewReader):
        self.disposition_id = reader.read_int()
        self.method = reader.read_int()


@dataclass
class ASClass:
    init_class: int
    traits: List[ASTrait]

    def __init__(self, reader: MemoryViewReader):
        self.init_class = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASScript:
    init: ABCMethodIndex
    traits: List[ASTrait]

    def __init__(self, reader: MemoryViewReader):
        self.init = reader.read_int()
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASMethodBody:
    method: ABCMethodIndex
    max_stack: int
    local_count: int
    init_scope_depth: int
    max_scope_depth: int
    code: memoryview
    exceptions: List[ASException]
    traits: List[ASTrait]

    def __init__(self, reader: MemoryViewReader):
        self.method = reader.read_int()
        self.max_stack = reader.read_int()
        self.local_count = reader.read_int()
        self.init_scope_depth = reader.read_int()
        self.max_scope_depth = reader.read_int()
        self.code = reader.read(reader.read_int())
        self.exceptions = read_array(reader, ASException)
        self.traits = read_array(reader, ASTrait)


@dataclass
class ASException:
    from_: int
    to: int
    target: int
    exc_type: ABCStringIndex
    var_name: ABCStringIndex

    def __init__(self, reader: MemoryViewReader):
        self.from_ = reader.read_int()
        self.to = reader.read_int()
        self.target = reader.read_int()
        self.exc_type = reader.read_int()
        self.var_name = reader.read_int()
