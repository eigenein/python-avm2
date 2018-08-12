from itertools import count
from struct import Struct
from typing import Union

D64 = Struct('<d')


class MemoryViewReader:
    """
    Reads a memory view as a structured stream.
    """

    def __init__(self, buffer: Union[memoryview, bytes]):
        self.buffer = buffer if isinstance(buffer, memoryview) else memoryview(buffer)
        self.position = 0

    def __repr__(self) -> str:
        return f'MemoryViewReader(buffer={self.buffer!r}, position={self.position!r})'

    def is_eof(self) -> bool:
        return self.position >= len(self.buffer)

    def read(self, size: int) -> memoryview:
        """
        Read the number of bytes.
        """
        return self.read_slice(slice(self.position, self.position + size))

    def read_all(self) -> memoryview:
        """
        Read everything until the end.
        """
        return self.read_slice(slice(self.position, None))

    def read_slice(self, slice_: slice) -> memoryview:
        """
        Read the slice of wrapped data. To be used internally.
        """
        buffer: memoryview = self.buffer[slice_]
        self.position += len(buffer)
        return buffer

    def skip(self, size: int) -> int:
        """
        Skip the number of bytes.
        """
        self.position += size
        return self.position

    def read_u8(self) -> int:
        """
        Read one-byte unsigned integer value.
        """
        value: int = self.buffer[self.position]
        self.position += 1
        return value

    def read_u16(self) -> int:
        """
        Read two-byte unsigned integer value.
        """
        return self.read_u8() | (self.read_u8() << 8)

    def read_u32(self) -> int:
        """
        Read four-byte unsigned integer value.
        """
        return self.read_u16() | (self.read_u16() << 16)

    def skip_rect(self):
        """
        Skip RECT record.
        """
        n_bits = self.read_u8()
        self.skip(((n_bits >> 3) * 4 - 3 + 8) // 8)  # `n_bits` times 4 minus 3 bits (already read)

    def read_until(self, sentinel: int) -> memoryview:
        """
        Read everything until the specified value.
        """
        for length in count():
            if self.buffer[self.position + length] == sentinel:
                value = self.buffer[self.position:self.position + length]
                self.position += length + 1
                return value

    def read_string(self) -> str:
        """
        Read null-terminated string.
        """
        return bytes(self.read_until(0)).decode('utf-8')

    def read_int(self, unsigned=True) -> int:
        """
        Read variable-length encoded 32-bit unsigned or signed integer value: ASVM2 u30, u32 and s32.
        """
        value = self.read_u8()
        if not value & 0x00000080:
            return value if unsigned else self.extend_sign(value, 0x00000040)
        value = (value & 0x0000007F) | (self.read_u8() << 7)
        if not value & 0x00004000:
            return value if unsigned else self.extend_sign(value, 0x00002000)
        value = (value & 0x00003FFF) | (self.read_u8() << 14)
        if not value & 0x00200000:
            return value if unsigned else self.extend_sign(value, 0x00100000)
        value = (value & 0x001FFFFF) | (self.read_u8() << 21)
        if not value & 0x10000000:
            return value if unsigned else self.extend_sign(value, 0x08000000)
        value = (value & 0x0FFFFFFF) | (self.read_u8() << 28)
        assert not value & 0x800000000, hex(value)
        return value if unsigned else self.extend_sign(value, 0x400000000)  # FIXME: unsure if that's the correct mask

    @staticmethod
    def extend_sign(value: int, mask: int) -> int:
        """
        Performs sign extension.
        https://stackoverflow.com/a/32031543/359730
        """
        # mask = 1 << (n_bit - 1)
        return (value & (mask - 1)) - (value & mask)

    def read_d64(self) -> float:
        # noinspection PyTypeChecker
        value, = D64.unpack(self.read(8))  # type: float
        return value
