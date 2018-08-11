from __future__ import annotations

import lzma
import zlib
from typing import Iterable, Union

from avm2.io import MemoryViewReader
from avm2.swf.enums import Signature
from avm2.swf.types import DoABCTag, DoABCTagFlags, Tag, TagType


def parse(input_: Union[memoryview, bytes]) -> Iterable[Tag]:
    """
    Parse SWF file and get an iterable of its tags.
    """
    if isinstance(input_, bytes):
        input_ = memoryview(input_)
    reader = MemoryViewReader(input_)
    signature = Signature(reader.read_u8())
    assert reader.read_u16() == 0x5357
    reader.skip(1)  # version
    reader.skip(4)  # file length
    reader = decompress(reader, signature)
    reader.skip_rect()
    reader.skip(4)  # frame rate and frame count
    return read_tags(reader)


def decompress(reader: MemoryViewReader, signature: Signature) -> MemoryViewReader:
    """
    Decompress the rest of an SWF file, depending on its signature.
    """
    if signature == Signature.UNCOMPRESSED:
        return reader
    if signature == Signature.LZMA:
        # https://stackoverflow.com/a/39777419/359730
        reader.skip(4)  # skip compressed length
        return MemoryViewReader(lzma.decompress(reader.read(5).tobytes() + b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + reader.read_all().tobytes()))
    if signature == Signature.ZLIB:
        return MemoryViewReader(zlib.decompress(reader.read_all()))
    assert False, 'unreachable code'


def read_tags(reader: MemoryViewReader) -> Iterable[Tag]:
    """
    Read tags from the stream and get an iterable of tags.
    """
    while True:
        code_length = reader.read_u16()
        length = code_length & 0b111111
        if length == 0x3F:
            # Long tag header.
            length = reader.read_u32()
        try:
            type_ = TagType(code_length >> 6)
        except ValueError:
            # Unknown tag type. Skip the tag.
            reader.skip(length)
        else:
            yield Tag(type_=type_, raw=reader.read(length))
            if type_ == TagType.END:
                break


# TODO: use dataclass and move to types.py.
def parse_do_abc_tag(tag: Tag) -> DoABCTag:
    """
    Parse DO_ABC tag.
    """
    assert tag.type_ == TagType.DO_ABC
    reader = MemoryViewReader(tag.raw)
    return DoABCTag(
        flags=DoABCTagFlags(reader.read_u32()),
        name=reader.read_string(),
        abc_file=reader.read_all(),
    )
