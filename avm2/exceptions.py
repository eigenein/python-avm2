from typing import Any


class ASException(Exception):
    pass


class ASReturnException(ASException):
    def __init__(self, return_value: Any):
        self.return_value = return_value


class ASJumpException(ASException):
    def __init__(self, offset: int):
        self.offset = offset


class ASError(ASException):
    def __init__(self, value: Any):
        self.value = value
