from __future__ import annotations

import lzma
import zlib
from io import BytesIO, SEEK_CUR
from struct import Struct
from typing import BinaryIO, Iterable

from avm2.swf.types import Signature, Tag, TagType
from avm2.utils import read_struct

HEADER_STRUCT = Struct('<BHBI')
CODE_LENGTH_STRUCT = Struct('<H')
TAG_LENGTH_STRUCT = Struct('<I')


def parse(io: BinaryIO) -> Iterable[Tag]:
    signature, ws, version, file_length = read_struct(io, HEADER_STRUCT)  # type: int, int, int, int
    assert ws == 0x5357
    io = decompress(io, Signature(signature))
    skip_rect(io)
    io.seek(4, SEEK_CUR)  # frame rate and frame count
    return read_tags(io)


def decompress(io: BinaryIO, signature: Signature) -> BinaryIO:
    if signature == Signature.UNCOMPRESSED:
        return io
    if signature == Signature.LZMA:
        # https://stackoverflow.com/a/39777419/359730
        io.seek(4, SEEK_CUR)  # skip compressed length
        return BytesIO(lzma.decompress(io.read(5) + b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + io.read()))
    if signature == Signature.ZLIB:
        return BytesIO(zlib.decompress(io.read()))
    assert False, 'unreachable code'


def skip_rect(io: BinaryIO):
    n_bits, = io.read(1)
    io.seek(((n_bits >> 3) * 4 - 3 + 8) // 8, SEEK_CUR)


def read_tags(io: BinaryIO) -> Iterable[Tag]:
    while True:
        code_length, = read_struct(io, CODE_LENGTH_STRUCT)  # type: int
        length = code_length & 0b111111
        if length == 0x3F:
            # Long tag header.
            length, = read_struct(io, TAG_LENGTH_STRUCT)  # type: int
        try:
            type_ = TagType(code_length >> 6)
        except ValueError:
            # Unknown tag type. Skip the tag.
            io.seek(length, SEEK_CUR)
        else:
            yield Tag(type_=type_, bytes_=io.read(length))
            if type_ == TagType.END:
                break
