from typing import BinaryIO, Iterable

from avm2.abc.parser import parse_abc_file
from avm2.abc.types import ABCFile
from avm2.swf.parser import parse
from avm2.swf.types import TagType


def parse_abc_files(io: BinaryIO) -> Iterable[ABCFile]:
    return (parse_abc_file(tag) for tag in parse(io) if tag.type_ == TagType.DO_ABC)
