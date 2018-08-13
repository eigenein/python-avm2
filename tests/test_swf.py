from __future__ import annotations

from avm2.swf.parser import parse_swf
from avm2.swf.types import DoABCTag, DoABCTagFlags


def test_parse_swf_1(swf_1: memoryview):
    assert len(list(parse_swf(swf_1))) == 5


def test_parse_swf_2(swf_2: memoryview):
    assert len(list(parse_swf(swf_2))) == 10


def test_parse_swf_3(swf_3: memoryview):
    assert len(list(parse_swf(swf_3))) == 1995


def test_parse_swf_4(swf_4: memoryview):
    assert len(list(parse_swf(swf_4))) == 9


def test_do_abc_tag_2(do_abc_tag: DoABCTag):
    assert do_abc_tag.flags == DoABCTagFlags.LAZY_INITIALIZE
    assert do_abc_tag.name == 'merged'
    assert do_abc_tag.abc_file
