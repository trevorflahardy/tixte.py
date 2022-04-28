"""
MIT License

Copyright (c) 2021 NextChai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Tuple, TypeVar
from typing_extensions import TypeAlias

__all__: Tuple[str, ...] = ('to_json',)

OverwrittenCoroutine: TypeAlias = Callable[..., Awaitable[Any]]
T = TypeVar('T')

try:
    import orjson

    _has_orjson: bool = True
except ImportError:
    _has_orjson: bool = False
    import json

if _has_orjson:

    def to_json(string: str) -> Dict[Any, Any]:
        return orjson.loads(string)

else:

    def to_json(string: str) -> Dict[Any, Any]:
        return json.loads(string)
