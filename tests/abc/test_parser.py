from avm2.abc.parser import ABCFile
from avm2.swf.parser import parse, parse_do_abc_tag
from avm2.swf.types import DoABCTagFlags, TagType
from tests.utils import SWF_2

# TODO: move all to test_abc.py?


def test_parse_do_abc_tag_2():
    tag, = (tag for tag in parse(SWF_2) if tag.type_ == TagType.DO_ABC)
    do_abc_tag = parse_do_abc_tag(tag)
    assert do_abc_tag.flags == DoABCTagFlags.LAZY_INITIALIZE
    assert do_abc_tag.name == 'merged'


def test_abc_file_2():
    tag, = (tag for tag in parse(SWF_2) if tag.type_ == TagType.DO_ABC)
    do_abc_tag = parse_do_abc_tag(tag)
    abc_file = ABCFile(do_abc_tag.abc_file)
    assert abc_file.major_version == 46
    assert abc_file.minor_version == 16
    assert len(abc_file.constant_pool.integers) == 463
    assert len(abc_file.constant_pool.unsigned_integers) == 27
    assert len(abc_file.constant_pool.doubles) == 376
    assert len(abc_file.constant_pool.strings) == 38136
    assert len(abc_file.constant_pool.namespaces) == 9048
    assert len(abc_file.constant_pool.ns_sets) == 1406
    assert len(abc_file.constant_pool.multinames) == 38608
