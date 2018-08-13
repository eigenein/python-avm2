from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from avm2.abc.enums import MethodFlags
from avm2.abc.instructions import read_instruction, undefined
from avm2.abc.types import ABCFile, ASMethod, ASMethodBody, ASScript, ASOptionDetail
from avm2.io import MemoryViewReader
from avm2.swf.enums import DoABCTagFlags
from avm2.swf.types import DoABCTag, Tag, TagType


class VirtualMachine:
    def __init__(self, abc_file: ABCFile):
        self.abc_file = abc_file
        self.method_bodies: Dict[int, int] = {method_body.method: i for i, method_body in enumerate(abc_file.method_bodies)}

    def execute_entry_point(self):
        """
        Execute the entry point, that is the last script in ABCFile.
        """
        self.execute_script(self.abc_file.scripts[-1])

    def execute_script(self, script: ASScript):
        """
        Execute the specified script.
        """
        self.execute_method(script.init, this=...)  # FIXME: what is `this`? Looks like a scope.

    def execute_method(self, index: int, *, this: Any, arguments: Iterable[Any] = ()):
        """
        Execute the specified method.
        """
        self.execute_method_body(self.method_bodies[index], this=this, arguments=arguments)

    def execute_method_body(self, index: int, *, this: Any, arguments: Iterable[Any] = ()):
        """
        Execute the method body.
        """
        method_body: ASMethodBody = self.abc_file.method_bodies[index]
        method: ASMethod = self.abc_file.methods[method_body.method]
        environment = self.create_method_environment(method, method_body, this, arguments)
        self.execute_code(method_body.code, environment)

    def create_method_environment(self, method: ASMethod, method_body: ASMethodBody, this: Any, arguments: Iterable[Any]) -> MethodEnvironment:
        """
        Create method execution environment: registers and stacks.
        """
        arguments = list(arguments)
        # There are `method_body_info.local_count` registers.
        registers: List[Any] = [...] * method_body.local_count
        # Register 0 holds the "this" object. This value is never null.
        registers[0] = this
        # Registers 1 through `method_info.param_count` holds parameter values coerced to the declared types
        # of the parameters.
        assert len(arguments) <= method.param_count
        registers[1:len(arguments) + 1] = arguments
        # If fewer than `method_body_info.local_count` values are supplied to the call then the remaining values are
        # either the values provided by default value declarations (optional arguments) or the value `undefined`.
        assert not method.options or len(method.options) <= method.param_count
        for i in range(len(arguments) + 1, method_body.local_count):
            registers[i] = self.get_optional_value(method.options[i - 1]) if i <= len(method.options) else undefined
        # If `NEED_REST` is set in `method_info.flags`, the `method_info.param_count + 1` register is set up to
        # reference an array that holds the superflous arguments.
        if MethodFlags.NEED_REST in method.flags:
            registers[method.param_count + 1] = arguments[method.param_count:]
        # If `NEED_ARGUMENTS` is set in `method_info.flags`, the `method_info.param_count + 1` register is set up
        # to reference an "arguments" object that holds all the actual arguments: see ECMA-262 for more
        # information.
        if MethodFlags.NEED_ARGUMENTS in method.flags:
            registers[method.param_count + 1] = arguments
        assert len(registers) == method_body.local_count
        return MethodEnvironment(registers=registers)

    def get_optional_value(self, option: ASOptionDetail) -> Any:
        """
        Get actual optional value.
        """
        raise NotImplementedError('get_optional_value')

    def execute_code(self, code: memoryview, environment: MethodEnvironment):
        """
        Execute the byte-code.
        """
        reader = MemoryViewReader(code)
        while True:
            # FIXME: cache already read instructions.
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
