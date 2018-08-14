from __future__ import annotations


class ASObject(dict):
    pass


class ASUndefined(ASObject):
    pass


undefined = ASUndefined()
