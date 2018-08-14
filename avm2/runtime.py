from __future__ import annotations


class ASObject:
    pass


class ASUndefined(ASObject):
    def __repr__(self):
        return f'{self.__class__.__name__}()'


undefined = ASUndefined()
