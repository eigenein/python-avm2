from typing import Iterable, List

from avm2.abc.instructions import Instruction, read_instruction
from avm2.abc.types import ABCFile, ASMethodBody
from avm2.io import MemoryViewReader


def test_abc_file(abc_file: ABCFile):
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

    assert len(read_method_body(abc_file.method_bodies[0])) == 103
    assert len(read_method_body(abc_file.method_bodies[1])) == 69
    assert len(read_method_body(abc_file.method_bodies[2])) == 69


def read_method_body(method_body: ASMethodBody) -> List[Instruction]:
    return list(read_instructions(MemoryViewReader(method_body.code)))


def read_instructions(reader: MemoryViewReader) -> Iterable[Instruction]:
    while not reader.is_eof():
        yield read_instruction(reader)
