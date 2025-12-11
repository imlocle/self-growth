from __future__ import annotations

from typing import Dict, Any
from dataclasses import asdict


class BaseModel:
    """
    Very lightweight base providing:
    - default to_dict() using dataclasses.asdict
    - to_dynamo() delegating to to_dict()
    Override to_dict() in subclasses if you need custom behavior.
    """

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_dynamo(self) -> Dict[str, Any]:
        return self.to_dict()
