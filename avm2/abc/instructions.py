from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Callable, ClassVar, Dict, Tuple, Type, TypeVar

import avm2
from avm2.abc.parser import read_array
from avm2.io import MemoryViewReader


def read_instruction(reader: MemoryViewReader) -> Instruction:
    # noinspection PyCallingNonCallable
    return opcode_to_instruction[reader.read_u8()](reader)


u8 = int
u30 = int
uint = int
s24 = int


@dataclass
class Instruction:
    readers: ClassVar[Dict[str, Callable[[MemoryViewReader], Any]]] = {
        'u8': MemoryViewReader.read_u8,
        'u30': MemoryViewReader.read_int,
        'uint': MemoryViewReader.read_u32,
        's24': MemoryViewReader.read_s24,
    }

    def __init__(self, reader: MemoryViewReader):
        for field in fields(self):
            setattr(self, field.name, self.readers[field.type](reader))

    def execute(self, environment: avm2.MethodEnvironment):
        raise NotImplementedError(self)


T = TypeVar('T', bound=Instruction)
opcode_to_instruction: Dict[int, Type[T]] = {}


def instruction(opcode: int) -> Callable[[], Type[T]]:
    def wrapper(class_: Type[T]) -> Type[T]:
        assert opcode not in opcode_to_instruction, opcode_to_instruction[opcode]
        opcode_to_instruction[opcode] = class_
        return dataclass(init=False)(class_)
    return wrapper


@instruction(160)
class Add(Instruction):
    pass


@instruction(197)
class AddInteger(Instruction):
    pass


@instruction(134)
class AsType(Instruction):
    index: u30


@instruction(135)
class AsTypeLate(Instruction):
    pass


@instruction(168)
class BitAnd(Instruction):
    pass


@instruction(151)
class BitNot(Instruction):
    pass


@instruction(169)
class BitOr(Instruction):
    pass


@instruction(170)
class BitXor(Instruction):
    pass


@instruction(65)
class Call(Instruction):
    arg_count: u30


@instruction(67)
class CallMethod(Instruction):
    index: u30
    arg_count: u30


@instruction(70)
class CallProperty(Instruction):
    index: u30
    arg_count: u30


@instruction(76)
class CallPropLex(Instruction):
    index: u30
    arg_count: u30


@instruction(79)
class CallPropVoid(Instruction):
    index: u30
    arg_count: u30


@instruction(68)
class CallStatic(Instruction):
    index: u30
    arg_count: u30


@instruction(69)
class CallSuper(Instruction):
    index: u30
    arg_count: u30


@instruction(78)
class CallSuperVoid(Instruction):
    index: u30
    arg_count: u30


@instruction(120)
class CheckFilter(Instruction):
    pass


@instruction(128)
class Coerce(Instruction):
    index: u30


@instruction(130)
class CoerceAny(Instruction):
    pass


@instruction(133)
class CoerceString(Instruction):
    pass


@instruction(66)
class Construct(Instruction):
    arg_count: u30


@instruction(74)
class ConstructProp(Instruction):
    index: u30
    arg_count: u30


@instruction(73)
class Construct(Instruction):
    arg_count: u30


@instruction(118)
class ConvertToBoolean(Instruction):
    pass


@instruction(115)
class ConvertToInteger(Instruction):
    pass


@instruction(117)
class ConvertToDouble(Instruction):
    pass


@instruction(119)
class ConvertToObject(Instruction):
    pass


@instruction(116)
class ConvertToUnsignedInteger(Instruction):
    pass


@instruction(112)
class ConvertToString(Instruction):
    pass


@instruction(239)
class Debug(Instruction):
    debug_type: u8
    index: u30
    reg: u8
    extra: u30


@instruction(241)
class DebugFile(Instruction):
    index: u30


@instruction(240)
class DebugLine(Instruction):
    linenum: u30


@instruction(148)
class DecLocal(Instruction):
    index: u30


@instruction(195)
class DecLocalInteger(Instruction):
    index: u30


@instruction(147)
class Decrement(Instruction):
    pass


@instruction(193)
class DecrementInteger(Instruction):
    pass


@instruction(106)
class DeleteProperty(Instruction):
    index: u30


@instruction(163)
class Divide(Instruction):
    pass


@instruction(42)
class Dup(Instruction):
    pass


@instruction(6)
class DXNS(Instruction):
    index: u30


@instruction(7)
class DXNSLate(Instruction):
    pass


@instruction(171)
class EqualsOperation(Instruction):
    pass


@instruction(114)
class EscXAttr(Instruction):
    pass


@instruction(113)
class EscXElem(Instruction):
    pass


@instruction(94)
class FindProperty(Instruction):
    index: u30


@instruction(93)
class FindPropStrict(Instruction):
    index: u30


@instruction(89)
class GetDescendants(Instruction):
    index: u30


@instruction(100)
class GetGlobalScope(Instruction):
    pass


@instruction(110)
class GetGlobalSlot(Instruction):
    slot_index: u30


@instruction(96)
class GetLex(Instruction):
    index: u30


@instruction(98)
class GetLocal(Instruction):
    index: u30


@instruction(208)
class GetLocal1(Instruction):
    def execute(self, environment: avm2.MethodEnvironment):
        environment.operand_stack.append(environment.registers[1])


@instruction(209)
class GetLocal2(Instruction):
    pass


@instruction(210)
class GetLocal3(Instruction):
    pass


@instruction(211)
class GetLocal4(Instruction):
    pass


@instruction(102)
class GetProperty(Instruction):
    index: u30


@instruction(101)
class GetScopeObject(Instruction):
    index: u8


@instruction(108)
class GetSlot(Instruction):
    slot_index: u30


@instruction(4)
class GetSuper(Instruction):
    index: u30


@instruction(176)
class GreaterEquals(Instruction):
    pass


@instruction(175)
class GreaterThan(Instruction):
    pass


@instruction(31)
class HasNext(Instruction):
    pass


@instruction(50)
class HasNext2(Instruction):
    object_reg: uint
    index_reg: uint


@instruction(19)
class IfEq(Instruction):
    offset: s24


@instruction(18)
class IfFalse(Instruction):
    offset: s24


@instruction(24)
class IfGE(Instruction):
    offset: s24


@instruction(23)
class IfGT(Instruction):
    offset: s24


@instruction(22)
class IfLE(Instruction):
    offset: s24


@instruction(21)
class IfLT(Instruction):
    offset: s24


@instruction(15)
class IfNGE(Instruction):
    offset: s24


@instruction(14)
class IfNGT(Instruction):
    offset: s24


@instruction(13)
class IfNLE(Instruction):
    offset: s24


@instruction(12)
class IfNLT(Instruction):
    offset: s24


@instruction(20)
class IfNE(Instruction):
    offset: s24


@instruction(25)
class IfStrictEq(Instruction):
    offset: s24


@instruction(26)
class IfStrictNE(Instruction):
    offset: s24


@instruction(17)
class IfTrue(Instruction):
    offset: s24


@instruction(180)
class In(Instruction):
    pass


@instruction(146)
class IncLocal(Instruction):
    index: u30


@instruction(194)
class IncLocalInteger(Instruction):
    index: u30


@instruction(145)
class Increment(Instruction):
    pass


@instruction(192)
class IncrementInteger(Instruction):
    pass


@instruction(104)
class InitProperty(Instruction):
    index: u30


@instruction(177)
class InstanceOf(Instruction):
    pass


@instruction(178)
class IsType(Instruction):
    index: u30


@instruction(179)
class IsTypeLate(Instruction):
    pass


@instruction(16)
class Jump(Instruction):
    offset: s24


@instruction(8)
class Kill(Instruction):
    index: u30


@instruction(9)
class Label(Instruction):
    pass


@instruction(174)
class LessEquals(Instruction):
    pass


@instruction(173)
class LessThan(Instruction):
    pass


@instruction(27)
class LookupSwitch(Instruction):
    default_offset: s24
    case_offsets: Tuple[s24, ...]

    # noinspection PyMissingConstructor
    def __init__(self, reader: MemoryViewReader):
        self.default_offset = reader.read_s24()
        case_count = reader.read_int()
        self.case_offsets = read_array(reader, MemoryViewReader.read_s24, case_count + 1)


@instruction(165)
class LeftShift(Instruction):
    pass


@instruction(164)
class Modulo(Instruction):
    pass


@instruction(162)
class Multiply(Instruction):
    pass


@instruction(199)
class MultiplyInteger(Instruction):
    pass


@instruction(144)
class Negate(Instruction):
    pass


@instruction(196)
class NegateInteger(Instruction):
    pass


@instruction(87)
class NewActivation(Instruction):
    pass


@instruction(86)
class NewArray(Instruction):
    arg_count: u30


@instruction(90)
class NewCatch(Instruction):
    index: u30


@instruction(88)
class NewClass(Instruction):
    index: u30


@instruction(64)
class NewFunction(Instruction):
    index: u30


@instruction(85)
class NewObject(Instruction):
    arg_count: u30


@instruction(30)
class NextName(Instruction):
    pass


@instruction(35)
class NextValue(Instruction):
    pass


@instruction(2)
class Nop(Instruction):
    pass


@instruction(150)
class Not(Instruction):
    pass


@instruction(41)
class Pop(Instruction):
    pass


@instruction(29)
class PopScope(Instruction):
    pass


@instruction(36)
class PushByte(Instruction):
    byte_value: u8


@instruction(47)
class PushDouble(Instruction):
    index: u30


@instruction(39)
class PushFalse(Instruction):
    pass


@instruction(45)
class PushInteger(Instruction):
    index: u30


@instruction(49)
class PushNamespace(Instruction):
    index: u30


@instruction(40)
class PushNaN(Instruction):
    pass


@instruction(32)
class PushNull(Instruction):
    pass


@instruction(48)
class PushScope(Instruction):
    pass


@instruction(37)
class PushShort(Instruction):
    value: u30


@instruction(44)
class PushString(Instruction):
    index: u30


@instruction(38)
class PushTrue(Instruction):
    pass


@instruction(46)
class PushUnsignedInteger(Instruction):
    index: u30


@instruction(33)
class PushUndefined(Instruction):
    pass


@instruction(28)
class PushWith(Instruction):
    pass


@instruction(72)
class ReturnValue(Instruction):
    pass


@instruction(71)
class ReturnVoid(Instruction):
    pass


@instruction(166)
class RightShift(Instruction):
    pass


@instruction(99)
class SetLocal(Instruction):
    index: u30


@instruction(212)
class SetLocal1(Instruction):
    pass


@instruction(213)
class SetLocal2(Instruction):
    pass


@instruction(214)
class SetLocal3(Instruction):
    pass


@instruction(215)
class SetLocal4(Instruction):
    pass


@instruction(111)
class SetGlobalSlot(Instruction):
    slot_index: u30


@instruction(97)
class SetProperty(Instruction):
    index: u30


@instruction(109)
class SetSlot(Instruction):
    slot_index: u30


@instruction(5)
class SetSuper(Instruction):
    index: u30


@instruction(172)
class StrictEquals(Instruction):
    pass


@instruction(161)
class Subtract(Instruction):
    pass


@instruction(198)
class SubtractInteger(Instruction):
    pass


@instruction(43)
class Swap(Instruction):
    pass


@instruction(3)
class Throw(Instruction):
    pass


@instruction(149)
class TypeOf(Instruction):
    pass


@instruction(167)
class UnsignedRightShift(Instruction):
    pass
