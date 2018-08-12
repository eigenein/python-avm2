from typing import Tuple

from avm2.abc.instructions import BaseInstruction, parse_code
from avm2.abc.types import ABCFile, MethodBodyInfo
from avm2.io import MemoryViewReader
from avm2.swf.parser import parse
from avm2.swf.types import DoABCTag, TagType
from tests.utils import SWF_2


def test_abc_file_2():
    tag, = (tag for tag in parse(SWF_2) if tag.type_ == TagType.DO_ABC)
    do_abc_tag = DoABCTag(tag.raw)
    reader = MemoryViewReader(do_abc_tag.abc_file)
    abc_file = ABCFile(reader)
    assert abc_file.major_version == 46
    assert abc_file.minor_version == 16
    assert len(abc_file.constant_pool.integers) == 463
    assert len(abc_file.constant_pool.unsigned_integers) == 27
    assert len(abc_file.constant_pool.doubles) == 376
    assert len(abc_file.constant_pool.strings) == 38136
    assert len(abc_file.constant_pool.namespaces) == 9048
    assert len(abc_file.constant_pool.ns_sets) == 1406
    assert len(abc_file.constant_pool.multinames) == 38608
    assert len(abc_file.methods) == 35243
    assert len(abc_file.metadata) == 196
    assert len(abc_file.instances) == 3739
    assert len(abc_file.classes) == 3739
    assert len(abc_file.scripts) == 3720
    assert len(abc_file.method_bodies) == 34687
    assert reader.is_eof()

    for instruction in parse_code(MemoryViewReader(abc_file.method_bodies[0].code)):
        print(instruction)

    assert len(parse_method_body(abc_file.method_bodies[0])) == 0


def parse_method_body(method_body_info: MethodBodyInfo) -> Tuple[BaseInstruction, ...]:
    return tuple(parse_code(MemoryViewReader(method_body_info.code)))
