from __future__ import annotations

from io import BytesIO, SEEK_CUR
from gzip import GzipFile
from lzma import LZMAFile
from struct import Struct
from typing import BinaryIO, Iterable, cast

from avm2.swf.types import Signature, Tag, TagType

HEADER_STRUCT = Struct('<BHBI')
CODE_LENGTH_STRUCT = Struct('<H')
TAG_LENGTH_STRUCT = Struct('<I')


def parse(io: BinaryIO) -> Iterable[Tag]:
    signature, ws, version, file_length = HEADER_STRUCT.unpack(io.read(HEADER_STRUCT.size))  # type: int, int, int, int
    assert ws == 0x5357
    io = decompress(io, Signature(signature))
    skip_rect(io)
    io.seek(4, SEEK_CUR)  # frame rate and frame count
    return read_tags(io)


def decompress(io: BinaryIO, signature: Signature) -> BinaryIO:
    if signature == Signature.LZMA:
        # https://stackoverflow.com/a/39777419/359730
        io.seek(4, SEEK_CUR)  # skip compressed length
        return cast(BinaryIO, LZMAFile(BytesIO(io.read(5) + b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF' + io.read())))
    if signature == Signature.ZLIB:
        return cast(BinaryIO, GzipFile(fileobj=io))
    return io


def skip_rect(io: BinaryIO):
    n_bits, = io.read(1)
    io.seek(((n_bits >> 3) * 4 - 3 + 8) // 8, SEEK_CUR)


def read_tags(io: BinaryIO) -> Iterable[Tag]:
    while True:
        code_length, = CODE_LENGTH_STRUCT.unpack(io.read(CODE_LENGTH_STRUCT.size))  # type: int
        length = code_length & 0b111111
        if length == 0x3F:
            # Long tag header.
            length, = TAG_LENGTH_STRUCT.unpack(io.read(TAG_LENGTH_STRUCT.size))  # type: int
        type_ = TagType(code_length >> 6)
        yield Tag(type_=type_, bytes_=io.read(length))
        if type_ == TagType.END:
            break
