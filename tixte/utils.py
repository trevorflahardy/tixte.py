import json
from typing import Any


def to_json(string: str) -> dict[Any, Any]:
    return json.loads(string)