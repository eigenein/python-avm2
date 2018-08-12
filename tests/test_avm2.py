from avm2 import execute_tag
from avm2.swf.parser import parse
from avm2.swf.types import TagType
from tests.utils import SWF_2


def test_execute_abc_file():
    for tag in parse(SWF_2):
        if tag.type_ == TagType.DO_ABC:
            execute_tag(tag).execute_entry_point()
