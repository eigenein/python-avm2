from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from avm2.abc.types import ABCClassIndex


@dataclass
class ASObject:
    class_index: Optional[ABCClassIndex] = None
    properties: Dict[Tuple[str, str], ASObject] = field(default_factory=dict)


@dataclass
class ASUndefined(ASObject):
    pass


undefined = ASUndefined()
