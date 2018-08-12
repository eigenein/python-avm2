from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from avm2.abc.enums import MethodFlags
from avm2.abc.instructions import read_instruction
from avm2.abc.types import ABCFile, Method, MethodBody, Script, OptionDetail
from avm2.io import MemoryViewReader
from avm2.swf.enums import DoABCTagFlags
from avm2.swf.types import DoABCTag, Tag, TagType


class VirtualMachine:
    def __init__(self, abc_file: ABCFile):
        self.abc_file = abc_file
        self.method_bodies: Dict[int, int] = {method_body.method: i for i, method_body in enumerate(abc_file.method_bodies)}

    def execute_entry_point(self):
        """
        Execute the entry point, that is the last script.
        """
        self.execute_script(self.abc_file.scripts[-1])

    def execute_script(self, script: Script):
        """
        Execute the specified script.
        """
        self.execute_method(script.init)

    def execute_method(self, index: int):
        """
        Execute the specified method.
        """
        self.execute_method_body(self.method_bodies[index])

    def execute_method_body(self, index: int, arguments: Iterable[Any] = ()):
        """
        Execute the method body.
        """
        method_body: MethodBody = self.abc_file.method_bodies[index]
        method: Method = self.abc_file.methods[method_body.method]
        environment = self.create_method_environment(method, arguments)
        self.execute_code(method_body.code, environment)

    def create_method_environment(self, method: Method, arguments: Iterable[Any]) -> MethodEnvironment:
        """
        Create method execution environment: registers and stacks.
        """
        # FIXME: something is wrong here, the test fails.
        if MethodFlags.NEED_REST in method.flags:
            registers = [..., *arguments[:method.param_count], list(arguments[method.param_count:])]
        elif MethodFlags.NEED_ARGUMENTS in method.flags:
            registers = [..., list(arguments)]
        else:
            registers = [..., *arguments[:method.param_count]]
            if MethodFlags.HAS_OPTIONAL in method.flags:
                registers.extend(self.get_optional_value(option) for option in method.options[len(registers):])
            registers.extend(Undefined for _ in range(len(registers), method.param_count))
        return MethodEnvironment(registers=registers)

    def get_optional_value(self, option: OptionDetail) -> Any:
        """
        Get actual optional value.
        """
        return ...

    def execute_code(self, code: memoryview, environment: MethodEnvironment):
        """
        Execute the byte-code.
        """
        reader = MemoryViewReader(code)
        while True:
            read_instruction(reader).execute(environment)


@dataclass
class MethodEnvironment:
    registers: List[Any]
    operand_stack: List[Any] = field(default_factory=list)
    scope_stack: List[Any] = field(default_factory=list)


def execute_tag(tag: Tag) -> VirtualMachine:
    """
    Parse and execute DO_ABC tag.
    """
    assert tag.type_ == TagType.DO_ABC
    return execute_do_abc_tag(DoABCTag(tag.raw))


def execute_do_abc_tag(do_abc_tag: DoABCTag) -> VirtualMachine:
    """
    Create a virtual machine and execute the tag.
    """
    machine = VirtualMachine(ABCFile(MemoryViewReader(do_abc_tag.abc_file)))
    if DoABCTagFlags.LAZY_INITIALIZE not in do_abc_tag.flags:
        machine.execute_entry_point()
    return machine


Undefined = object()  # FIXME
