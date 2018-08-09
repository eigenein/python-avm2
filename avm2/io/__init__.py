class MemoryViewIO:
    def __init__(self, buffer: memoryview):
        self.buffer = buffer
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
