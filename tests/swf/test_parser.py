from __future__ import annotations

import pytest

from avm2.swf.parser import parse, parse_do_abc_tag
from avm2.swf.types import DoABCTagFlags, TagType
from tests.utils import SWF_1, SWF_2, SWF_3, SWF_4


@pytest.mark.parametrize('buffer, n_tags', [
    (SWF_1, 5),
    (SWF_2, 10),
    (SWF_3, 1995),
    (SWF_4, 9),
])
def test_parse(buffer: memoryview, n_tags: int):
    assert len(list(parse(buffer))) == n_tags


def test_parse_do_abc_tag_2():
    tag, = (tag for tag in parse(SWF_2) if tag.type_ == TagType.DO_ABC)
    do_abc_tag = parse_do_abc_tag(tag)
    assert do_abc_tag.flags == DoABCTagFlags.LAZY_INITIALIZE
    assert do_abc_tag.name == 'merged'
