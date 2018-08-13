from pathlib import Path

from pytest import fixture

import tests
from avm2.abc.types import ABCFile
from avm2.io import MemoryViewReader
from avm2.swf.enums import TagType
from avm2.swf.parser import parse_swf
from avm2.swf.types import DoABCTag, Tag
from avm2.vm import VirtualMachine

base_path = Path(tests.__file__).parent.parent / 'data'


@fixture(scope='session')
def swf_1() -> memoryview:
    return memoryview(bytes.fromhex(
        '465753034F0000007800055F00000FA000000C01004302FFFFFFBF0023000000'
        '010070FB49970D0C7D50000114000000000125C9920D21ED488765303B6DE1D8'
        'B40000860606010001000040000000'
    ))


@fixture(scope='session')
def swf_2() -> memoryview:
    return memoryview((base_path / 'heroes.swf').read_bytes())


@fixture(scope='session')
def swf_3() -> memoryview:
    return memoryview((base_path / 'Farm_d_13_9_2_2198334.swf').read_bytes())


@fixture(scope='session')
def swf_4() -> memoryview:
    return memoryview((base_path / 'EpicGame.swf').read_bytes())


@fixture(scope='session')
def raw_do_abc_tag(swf_2: memoryview) -> Tag:
    for tag in parse_swf(swf_2):
        if tag.type_ == TagType.DO_ABC:
            return tag


@fixture(scope='session')
def do_abc_tag(raw_do_abc_tag: Tag) -> DoABCTag:
    return DoABCTag(raw_do_abc_tag.raw)


@fixture(scope='session')
def abc_file(do_abc_tag: DoABCTag) -> ABCFile:
    return ABCFile(MemoryViewReader(do_abc_tag.abc_file))


@fixture(scope='session')
def machine(abc_file: ABCFile) -> VirtualMachine:
    return VirtualMachine(abc_file)
