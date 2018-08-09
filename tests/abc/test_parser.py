from avm2.abc.parser import parse_abc_file
from avm2.swf.parser import parse, parse_do_abc_tag
from avm2.swf.types import TagType
from tests.utils import SWF_2


def test_parse_do_abc_tag_2():
    tag, = (tag for tag in parse(SWF_2) if tag.type_ == TagType.DO_ABC)
    do_abc_tag = parse_do_abc_tag(tag)
    abc_file = parse_abc_file(do_abc_tag.abc_file)
    assert abc_file.major_version == 46
    assert abc_file.minor_version == 16
