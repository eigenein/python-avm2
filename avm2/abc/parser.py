from avm2.swf.types import Tag, TagType
from avm2.abc.types import ABCFile


def parse_abc_file(tag: Tag) -> ABCFile:
    assert tag.type_ == TagType.DO_ABC
