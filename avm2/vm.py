from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple

import avm2.abc.instructions
from avm2.abc.enums import MethodFlags, TraitKind, ConstantKind
from avm2.abc.types import ABCFile, ABCClassIndex, ABCMethodIndex, ABCMethodBodyIndex, ASMethod, ASMethodBody, ASOptionDetail, ASScript
from avm2.io import MemoryViewReader
from avm2.runtime import undefined
from avm2.swf.types import DoABCTag, Tag, TagType
from avm2.exceptions import ASReturnException, ASJumpException


class VirtualMachine:
    def __init__(self, abc_file: ABCFile):
        self.abc_file = abc_file

        # Quick access.
        self.constant_pool = abc_file.constant_pool
        self.strings = self.constant_pool.strings
        self.multinames = self.constant_pool.multinames
        self.integers = self.constant_pool.integers
        self.doubles = self.constant_pool.doubles

        # Linking.
        self.method_to_body = self.link_method_bodies()
        self.name_to_class = dict(self.link_class_names())
        self.name_to_method = dict(self.link_method_names())

    # Linking.
    # ------------------------------------------------------------------------------------------------------------------

    def link_method_bodies(self) -> Dict[ABCMethodIndex, ABCMethodBodyIndex]:
        """
        Link methods and methods bodies.
        """
        return {method_body.method: index for index, method_body in enumerate(self.abc_file.method_bodies)}

    def link_class_names(self) -> Iterable[Tuple[str, ABCClassIndex]]:
        """
        Link class names and class indices.
        """
        for index, instance in enumerate(self.abc_file.instances):
            assert instance.name
            yield self.multinames[instance.name].qualified_name(self.constant_pool), index

    def link_method_names(self) -> Iterable[Tuple[str, ABCMethodIndex]]:
        """
        Link method names and method indices.
        """
        for instance, class_ in zip(self.abc_file.instances, self.abc_file.classes):
            qualified_class_name = self.multinames[instance.name].qualified_name(self.constant_pool)
            for trait in class_.traits:
                if trait.kind in (TraitKind.GETTER, TraitKind.SETTER, TraitKind.METHOD):
                    qualified_trait_name = self.multinames[trait.name].qualified_name(self.constant_pool)
                    yield f'{qualified_class_name}.{qualified_trait_name}', trait.data.method

    # Lookups.
    # ------------------------------------------------------------------------------------------------------------------

    def lookup_class(self, qualified_name: str) -> ABCClassIndex:
        return self.name_to_class[qualified_name]

    def lookup_method(self, qualified_name: str) -> ABCMethodIndex:
        return self.name_to_method[qualified_name]

    # Execution.
    # ------------------------------------------------------------------------------------------------------------------

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

    def execute_method(self, index: ABCMethodIndex, this: Any, *args) -> Any:
        """
        Execute the specified method and get a return value.
        """
        return self.execute_method_body(self.method_to_body[index], this, *args)

    def execute_method_body(self, index: ABCMethodBodyIndex, this: Any, *args) -> Any:
        """
        Execute the method body and get a return value.
        """
        method_body: ASMethodBody = self.abc_file.method_bodies[index]
        method: ASMethod = self.abc_file.methods[method_body.method]
        environment = self.create_method_environment(method, method_body, this, *args)
        return self.execute_code(method_body.code, environment)

    def execute_code(self, code: memoryview, environment: MethodEnvironment) -> Any:
        """
        Execute the byte-code and get a return value.
        """
        reader = MemoryViewReader(code)
        while True:
            try:
                # FIXME: cache already read instructions.
                avm2.abc.instructions.read_instruction(reader).execute(self, environment)
            except ASReturnException as e:
                return e.return_value
            except ASJumpException as e:
                reader.position += e.offset

    # Unclassified.
    # ------------------------------------------------------------------------------------------------------------------

    def create_method_environment(self, method: ASMethod, method_body: ASMethodBody, this: Any, *args) -> MethodEnvironment:
        """
        Create method execution environment: registers and stacks.
        """
        # There are `method_body_info.local_count` registers.
        registers: List[Any] = [undefined] * method_body.local_count
        # Register 0 holds the "this" object. This value is never null.
        registers[0] = this
        # Registers 1 through `method_info.param_count` holds parameter values coerced to the declared types
        # of the parameters.
        assert len(args) <= method.param_count
        registers[1:len(args) + 1] = args
        # If fewer than `method_body_info.local_count` values are supplied to the call then the remaining values are
        # either the values provided by default value declarations (optional arguments) or the value `undefined`.
        if method.options:
            assert len(method.options) <= method.param_count
            for i, option in zip(range(len(args) + 1, method_body.local_count), method.options):
                registers[i] = self.get_optional_value(option)
        # If `NEED_REST` is set in `method_info.flags`, the `method_info.param_count + 1` register is set up to
        # reference an array that holds the superflous arguments.
        if MethodFlags.NEED_REST in method.flags:
            registers[method.param_count + 1] = args[method.param_count:]
        # If `NEED_ARGUMENTS` is set in `method_info.flags`, the `method_info.param_count + 1` register is set up
        # to reference an "arguments" object that holds all the actual arguments: see ECMA-262 for more
        # information.
        if MethodFlags.NEED_ARGUMENTS in method.flags:
            registers[method.param_count + 1] = args
        assert len(registers) == method_body.local_count
        return MethodEnvironment(registers=registers)

    def get_optional_value(self, option: ASOptionDetail) -> Any:
        """
        Get actual optional value.
        """
        if option.kind == ConstantKind.TRUE:
            return True
        if option.kind == ConstantKind.FALSE:
            return False
        if option.kind == ConstantKind.NULL:
            return None
        if option.kind == ConstantKind.UNDEFINED:
            return undefined
        if option.kind == ConstantKind.INT:
            return self.integers[option.value]
        raise NotImplementedError(option.kind)


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
    return VirtualMachine(ABCFile(MemoryViewReader(do_abc_tag.abc_file)))
