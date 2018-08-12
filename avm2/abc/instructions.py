from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Callable, Dict, Iterable, Type, TypeVar

from avm2.io import MemoryViewReader


def parse_code(reader: MemoryViewReader) -> Iterable[BaseInstruction]:
    while not reader.is_eof():
        class_ = opcode_to_instruction[reader.read_u8()]
        # noinspection PyCallingNonCallable
        yield class_(*(argument_readers[field.type](reader) for field in fields(class_)))


u8 = int
u30 = int
uint = int
s24 = int


argument_readers: Dict[str, Callable[[MemoryViewReader], Any]] = {
    u8.__name__: MemoryViewReader.read_u8,
    u30.__name__: MemoryViewReader.read_int,
    uint.__name__: MemoryViewReader.read_u32,
    s24.__name__: MemoryViewReader.read_s24,
}


@dataclass
class BaseInstruction:
    pass


T = TypeVar('T', bound=BaseInstruction)
opcode_to_instruction: Dict[int, Type[T]] = {}


def instruction(opcode: int) -> Callable[[], Type[T]]:
    def wrapper(class_: Type[T]) -> Type[T]:
        assert opcode not in opcode_to_instruction
        opcode_to_instruction[opcode] = class_
        return class_
    return wrapper


@instruction(160)
@dataclass
class AddInstruction(BaseInstruction):
    pass


@instruction(197)
@dataclass
class AddIntegerInstruction(BaseInstruction):
    pass


@instruction(134)
@dataclass
class AsTypeInstruction(BaseInstruction):
    index: u30


@instruction(135)
@dataclass
class AsTypeLateInstruction(BaseInstruction):
    pass


@instruction(168)
@dataclass
class BitAndInstruction(BaseInstruction):
    pass


@instruction(151)
@dataclass
class BitNotInstruction(BaseInstruction):
    pass


@instruction(169)
@dataclass
class BitOrInstruction(BaseInstruction):
    pass


@instruction(170)
@dataclass
class BitXorInstruction(BaseInstruction):
    pass


@instruction(65)
@dataclass
class CallInstruction(BaseInstruction):
    arg_count: u30


@instruction(67)
@dataclass
class CallMethodInstruction(BaseInstruction):
    index: int
    arg_count: u30


@instruction(70)
@dataclass
class CallPropertyInstruction(BaseInstruction):
    index: int
    arg_count: u30


@instruction(76)
@dataclass
class CallPropLexInstruction(BaseInstruction):
    index: u30
    arg_count: u30


@instruction(79)
@dataclass
class CallPropVoidInstruction(BaseInstruction):
    index: u30
    arg_count: u30


@instruction(68)
@dataclass
class CallStaticInstruction(BaseInstruction):
    index: u30
    arg_count: u30


@instruction(69)
@dataclass
class CallSuperInstruction(BaseInstruction):
    index: u30
    arg_count: u30


@instruction(78)
@dataclass
class CallSuperVoidInstruction(BaseInstruction):
    index: u30
    arg_count: u30


@instruction(120)
@dataclass
class CheckFilterInstruction(BaseInstruction):
    pass


@instruction(128)
@dataclass
class CoerceInstruction(BaseInstruction):
    index: u30


@instruction(130)
@dataclass
class CoerceAnyInstruction(BaseInstruction):
    pass


@instruction(133)
@dataclass
class CoerceStringInstruction(BaseInstruction):
    pass


@instruction(66)
@dataclass
class ConstructInstruction(BaseInstruction):
    arg_count: u30


@instruction(74)
@dataclass
class ConstructPropInstruction(BaseInstruction):
    index: u30
    arg_count: u30


@instruction(73)
@dataclass
class ConstructInstruction(BaseInstruction):
    arg_count: u30


@instruction(118)
@dataclass
class ConvertBooleanInstruction(BaseInstruction):
    pass


@instruction(115)
@dataclass
class ConvertIntegerInstruction(BaseInstruction):
    pass


@instruction(117)
@dataclass
class ConvertDoubleInstruction(BaseInstruction):
    pass


@instruction(119)
@dataclass
class ConvertObjectInstruction(BaseInstruction):
    pass


@instruction(116)
@dataclass
class ConvertUnsignedIntegerInstruction(BaseInstruction):
    pass


@instruction(112)
@dataclass
class ConvertStringInstruction(BaseInstruction):
    pass


@instruction(239)
@dataclass
class DebugInstruction(BaseInstruction):
    debug_type: u8
    index: u30
    reg: u8
    extra: u30


@instruction(241)
@dataclass
class DebugFileInstruction(BaseInstruction):
    index: u30


@instruction(240)
@dataclass
class DebugLineInstruction(BaseInstruction):
    linenum: u30


@instruction(148)
@dataclass
class DecLocalInstruction(BaseInstruction):
    index: u30


@instruction(195)
@dataclass
class DecLocalIntegerInstruction(BaseInstruction):
    index: u30


@instruction(147)
@dataclass
class DecrementInstruction(BaseInstruction):
    pass


@instruction(193)
@dataclass
class DecrementIntegerInstruction(BaseInstruction):
    pass


@instruction(106)
@dataclass
class DeletePropertyInstruction(BaseInstruction):
    index: u30


@instruction(163)
@dataclass
class DivideInstruction(BaseInstruction):
    pass


@instruction(42)
@dataclass
class DupInstruction(BaseInstruction):
    pass


@instruction(6)
@dataclass
class DXNSInstruction(BaseInstruction):
    index: u30


@instruction(7)
@dataclass
class DXNSLateInstruction(BaseInstruction):
    pass


@instruction(171)
@dataclass
class EqualsOperation(BaseInstruction):
    pass


@instruction(114)
@dataclass
class EscXAttrInstruction(BaseInstruction):
    pass


@instruction(113)
@dataclass
class EscXElemInstruction(BaseInstruction):
    pass


@instruction(94)
@dataclass
class FindPropertyInstruction(BaseInstruction):
    index: u30


@instruction(93)
@dataclass
class FindPropStrictInstruction(BaseInstruction):
    index: u30


@instruction(89)
@dataclass
class GetDescendantsInstruction(BaseInstruction):
    index: u30


@instruction(100)
@dataclass
class GetGlobalScopeInstruction(BaseInstruction):
    pass


@instruction(110)
@dataclass
class GetGlobalSlotInstruction(BaseInstruction):
    slot_index: u30


@instruction(96)
@dataclass
class GetLexInstruction(BaseInstruction):
    index: u30


@instruction(98)
@dataclass
class GetLocalInstruction(BaseInstruction):
    index: u30


@instruction(208)
@dataclass
class GetLocal1Instruction(BaseInstruction):
    pass


@instruction(209)
@dataclass
class GetLocal2Instruction(BaseInstruction):
    pass


@instruction(210)
@dataclass
class GetLocal3Instruction(BaseInstruction):
    pass


@instruction(211)
@dataclass
class GetLocal4Instruction(BaseInstruction):
    pass


@instruction(102)
@dataclass
class GetPropertyInstruction(BaseInstruction):
    index: u30


@instruction(101)
@dataclass
class GetScopeObjectInstruction(BaseInstruction):
    index: u8


@instruction(108)
@dataclass
class GetSlotInstruction(BaseInstruction):
    slot_index: u30


@instruction(4)
@dataclass
class GetSuperInstruction(BaseInstruction):
    index: u30


@instruction(176)
@dataclass
class GreaterEqualsInstruction(BaseInstruction):
    pass


@instruction(175)
@dataclass
class GreaterThanInstruction(BaseInstruction):
    pass


@instruction(31)
@dataclass
class HasNextInstruction(BaseInstruction):
    pass


@instruction(50)
@dataclass
class HasNext2Instruction(BaseInstruction):
    object_reg: uint
    index_reg: uint


@instruction(19)
@dataclass
class IfEqInstruction(BaseInstruction):
    offset: s24


@instruction(18)
@dataclass
class IfFalseInstruction(BaseInstruction):
    offset: s24


@instruction(24)
@dataclass
class IfGEInstruction(BaseInstruction):
    offset: s24


@instruction(23)
@dataclass
class IfGTInstruction(BaseInstruction):
    offset: s24


@instruction(22)
@dataclass
class IfLEInstruction(BaseInstruction):
    offset: s24


@instruction(21)
@dataclass
class IfLTInstruction(BaseInstruction):
    offset: s24


@instruction(15)
@dataclass
class IfNGEInstruction(BaseInstruction):
    offset: s24


@instruction(14)
@dataclass
class IfNGTInstruction(BaseInstruction):
    offset: s24


@instruction(13)
@dataclass
class IfNLEInstruction(BaseInstruction):
    offset: s24


@instruction(12)
@dataclass
class IfNLTInstruction(BaseInstruction):
    offset: s24


@instruction(20)
@dataclass
class IfNEInstruction(BaseInstruction):
    offset: s24
