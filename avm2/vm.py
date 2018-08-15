from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple, Union

import avm2.abc.instructions
from avm2.abc.enums import ConstantKind, MethodFlags, TraitKind
from avm2.abc.types import (ABCClassIndex, ABCFile, ABCMethodBodyIndex, ABCMethodIndex, ABCScriptIndex, ASMethodBody,
    ASOptionDetail)
from avm2.exceptions import ASJumpException, ASReturnException
from avm2.io import MemoryViewReader
from avm2.runtime import ASObject, undefined
from avm2.swf.types import DoABCTag, Tag, TagType


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
        self.method_to_body = self.link_methods_to_bodies()
        self.name_to_class = dict(self.link_names_to_classes())
        self.name_to_method = dict(self.link_names_to_methods())
        self.class_to_script = dict(self.link_classes_to_scripts())
        # TODO: method to class in order to initialise class.

        # Runtime.
        self.class_objects: Dict[ABCClassIndex, ASObject] = dict()  # FIXME: unsure.
        self.script_objects: Dict[ABCScriptIndex, ASObject] = dict()  # FIXME: unsure.
        self.global_object = ASObject({'Object': ASObject})  # FIXME: unsure.

    # Linking.
    # ------------------------------------------------------------------------------------------------------------------

    def link_methods_to_bodies(self) -> Dict[ABCMethodIndex, ABCMethodBodyIndex]:
        """
        Link methods and methods bodies.
        """
        return {method_body.method_index: index for index, method_body in enumerate(self.abc_file.method_bodies)}

    def link_names_to_classes(self) -> Iterable[Tuple[str, ABCClassIndex]]:
        """
        Link class names and class indices.
        """
        for index, instance in enumerate(self.abc_file.instances):
            assert instance.name_index
            yield self.multinames[instance.name_index].qualified_name(self.constant_pool), index

    def link_names_to_methods(self) -> Iterable[Tuple[str, ABCMethodIndex]]:
        """
        Link method names and method indices.
        """
        for instance, class_ in zip(self.abc_file.instances, self.abc_file.classes):
            qualified_class_name = self.multinames[instance.name_index].qualified_name(self.constant_pool)
            for trait in class_.traits:
                if trait.kind in (TraitKind.GETTER, TraitKind.SETTER, TraitKind.METHOD):
                    qualified_trait_name = self.multinames[trait.name_index].qualified_name(self.constant_pool)
                    yield f'{qualified_class_name}.{qualified_trait_name}', trait.data.method_index

    def link_classes_to_scripts(self) -> Iterable[Tuple[ABCClassIndex, ABCScriptIndex]]:
        for script_index, script in enumerate(self.abc_file.scripts):
            for trait in script.traits:
                if trait.kind == TraitKind.CLASS:
                    yield trait.data.class_index, script_index

    # Lookups.
    # ------------------------------------------------------------------------------------------------------------------

    def lookup_class(self, qualified_name: str) -> ABCClassIndex:
        return self.name_to_class[qualified_name]

    def lookup_method(self, qualified_name: str) -> ABCMethodIndex:
        return self.name_to_method[qualified_name]

    # Scripts.
    # ------------------------------------------------------------------------------------------------------------------

    def init_script(self, script_index: ABCScriptIndex):
        """
        Initialise the specified script.
        """
        if script_index in self.script_objects:
            return
        script_object = ASObject()
        self.call_method(self.abc_file.scripts[script_index].init_index, script_object)  # TODO: what is `this`?
        self.script_objects[script_index] = script_object

    # Classes.
    # ------------------------------------------------------------------------------------------------------------------

    def init_class(self, class_index: ABCClassIndex):
        class_object = ASObject()
        self.class_objects[class_index] = class_object
        self.call_method(self.abc_file.classes[class_index].init_index, class_object)
        # TODO: the scope stack is saved by the created ClassClosure.

    def new_instance(self, index_or_name: Union[ABCClassIndex, str], *args) -> ASObject:
        if isinstance(index_or_name, int):
            class_index = ABCClassIndex(index_or_name)
        elif isinstance(index_or_name, str):
            class_index = self.lookup_class(index_or_name)
        else:
            raise ValueError(index_or_name)
        self.init_script(self.class_to_script[class_index])

        instance = ASObject()
        self.call_method(self.abc_file.instances[class_index].init_index, instance, *args)
        return instance

    # Execution.
    # ------------------------------------------------------------------------------------------------------------------

    def call_entry_point(self):
        """
        Call the entry point, that is the last script in ABCFile.
        """
        self.init_script(ABCScriptIndex(-1))

    def call_method(self, index_or_name: Union[ABCMethodIndex, str], this: Any, *args) -> Any:
        """
        Call the specified method and get a return value.
        """
        if isinstance(index_or_name, int):
            index = ABCMethodIndex(index_or_name)
        elif isinstance(index_or_name, str):
            index = self.lookup_method(index_or_name)
        else:
            raise ValueError(index_or_name)
        method_body = self.abc_file.method_bodies[self.method_to_body[index]]
        environment = self.create_method_environment(method_body, this, *args)
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

    def create_method_environment(self, method_body: ASMethodBody, this: Any, *args) -> MethodEnvironment:
        """
        Create method execution environment: registers and stacks.
        """
        method = self.abc_file.methods[method_body.method_index]
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
        return MethodEnvironment(registers=registers, scope_stack=[self.global_object])

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
    scope_stack: List[Any]
    operand_stack: List[Any] = field(default_factory=list)


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
