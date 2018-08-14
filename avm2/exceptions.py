from typing import Any


class ASException(Exception):
    pass


class ASReturnException(ASException):
    def __init__(self, return_value: Any):
        self.return_value = return_value
