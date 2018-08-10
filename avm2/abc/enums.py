from enum import IntEnum


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
