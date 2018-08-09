from io import BytesIO

from avm2.abc.types import ABCFile
from avm2.helpers import read_value
from avm2.swf.parser import U16_STRUCT


def parse_abc_file(raw: bytes) -> ABCFile:
    """
    Parse abcFile structure.
    """
    io = BytesIO(raw)
    return ABCFile(
        minor_version=read_value(io, U16_STRUCT),
        major_version=read_value(io, U16_STRUCT),
        # TODO
    )
