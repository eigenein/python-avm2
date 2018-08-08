from io import BytesIO

from avm2.abc.types import DoABCTag, DoABCTagFlags
from avm2.utils import parse_do_abc_tags
from tests.utils import SWF_2


def test_parse_do_abc_tag_2():
    tag, = parse_do_abc_tags(BytesIO(SWF_2))  # type: DoABCTag
    assert tag.major_version == 46
    assert tag.minor_version == 16
    assert tag.name == 'merged'
    assert tag.flags == DoABCTagFlags.LAZY_INITIALIZE
