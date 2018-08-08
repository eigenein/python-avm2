from typing import BinaryIO, Iterable

from avm2.abc.parser import parse_do_abc_tag
from avm2.abc.types import DoABCTag
from avm2.swf.parser import parse
from avm2.swf.types import TagType


def parse_do_abc_tags(io: BinaryIO) -> Iterable[DoABCTag]:
    return (parse_do_abc_tag(tag) for tag in parse(io) if tag.type_ == TagType.DO_ABC)
