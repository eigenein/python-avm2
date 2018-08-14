from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ASObject:
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ASUndefined(ASObject):
    pass


undefined = ASUndefined()
