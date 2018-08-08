from io import BytesIO

from avm2.abc.types import DoABCTag, DoABCTagFlags
from avm2.helpers import read_string, read_value
from avm2.swf.parser import U16_STRUCT, U32_STRUCT
from avm2.swf.types import Tag, TagType


def parse_do_abc_tag(tag: Tag) -> DoABCTag:
    assert tag.type_ == TagType.DO_ABC
    io = BytesIO(tag.raw)
    return DoABCTag(
        flags=DoABCTagFlags(read_value(io, U32_STRUCT)),
        name=read_string(io),
        minor_version=read_value(io, U16_STRUCT),
        major_version=read_value(io, U16_STRUCT),
        # TODO
    )
