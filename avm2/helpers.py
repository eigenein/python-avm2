from struct import Struct
from typing import Any, BinaryIO, Iterable, Tuple


def read_struct(io: BinaryIO, struct: Struct) -> Tuple:
    return struct.unpack(io.read(struct.size))


def read_value(io: BinaryIO, struct: Struct) -> Any:
    value, = read_struct(io, struct)
    return value


def read_until(io: BinaryIO, sentinel: int) -> Iterable[int]:
    while True:
        byte, = io.read(1)
        if byte == sentinel:
            break
        yield byte


def read_string(io: BinaryIO) -> str:
    return bytes(read_until(io, 0)).decode('utf-8')
