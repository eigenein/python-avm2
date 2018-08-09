from io import SEEK_CUR, SEEK_SET, SEEK_END
from typing import Optional


class MemoryViewIO:
    def __init__(self, buffer: memoryview):
        self.buffer = buffer
        self.position = 0

    def read(self, size: Optional[int] = None) -> memoryview:
        if size is not None:
            buffer: memoryview = self.buffer[self.position:self.position + size]
        else:
            buffer: memoryview = self.buffer[self.position:]
        self.position += len(buffer)
        return buffer

    def seek(self, offset: int, whence: int):
        if whence == SEEK_CUR:
            self.position += offset
        elif whence == SEEK_SET:
            self.position = offset
        elif whence == SEEK_END:
            self.position = len(self.buffer) + offset
        else:
            raise ValueError(whence)
