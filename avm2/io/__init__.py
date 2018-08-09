from itertools import count
from typing import Iterable, Union


class MemoryViewReader:
    def __init__(self, buffer: Union[memoryview, bytes]):
        self.buffer = buffer if isinstance(buffer, memoryview) else memoryview(buffer)
        self.position = 0

    def read(self, size: int) -> memoryview:
        return self.read_slice(slice(self.position, self.position + size))

    def read_all(self) -> memoryview:
        return self.read_slice(slice(self.position, None))

    def read_slice(self, slice_: slice) -> memoryview:
        buffer: memoryview = self.buffer[slice_]
        self.position += len(buffer)
        return buffer

    def skip(self, size: int) -> int:
        self.position += size
        return self.position

    def read_u8(self) -> int:
        value: int = self.buffer[self.position]
        self.position += 1
        return value

    def read_u16(self) -> int:
        return self.read_u8() | (self.read_u8() << 8)

    def read_u32(self) -> int:
        return self.read_u16() | (self.read_u16() << 16)

    def skip_rect(self):
        n_bits = self.read_u8()
        self.skip(((n_bits >> 3) * 4 - 3 + 8) // 8)  # `n_bits` times 4 minus 3 bits (already read)

    def read_until(self, sentinel: int) -> Iterable[int]:
        for length in count():
            if self.buffer[self.position + length] == sentinel:
                value = self.buffer[self.position:self.position + length]
                self.position += length + 1
                return value

    def read_string(self) -> str:
        return bytes(self.read_until(0)).decode('utf-8')
