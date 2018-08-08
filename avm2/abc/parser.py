from io import BytesIO
from struct import Struct

from avm2.swf.types import Tag, TagType
from avm2.abc.types import ABCFile, ABCFileFlags
from avm2.helpers import read_string, read_value

U16 = Struct('<H')
U32 = Struct('<I')


def parse_abc_file(tag: Tag) -> ABCFile:
    assert tag.type_ == TagType.DO_ABC
    io = BytesIO(tag.bytes_)
    return ABCFile(
        flags=ABCFileFlags(read_value(io, U32)),
        name=read_string(io),
        minor_version=read_value(io, U16),
        major_version=read_value(io, U16),
        # TODO
    )
