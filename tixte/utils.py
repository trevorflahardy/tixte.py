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

import datetime
from typing import Any, Dict, Tuple

__all__: Tuple[str, ...] = ('to_json',)


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


def parse_time(time_strp: str) -> datetime.datetime:
    return datetime.datetime.strptime(time_strp, '%Y-%m-%dT%H:%M:%S.%fZ')