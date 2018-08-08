from struct import Struct
from typing import BinaryIO, Tuple


def read_struct(io: BinaryIO, struct: Struct) -> Tuple:
    return struct.unpack(io.read(struct.size))
