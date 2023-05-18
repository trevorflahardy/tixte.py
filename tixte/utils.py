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
from typing import Any, Callable, Dict, Iterable, Optional, Tuple, Type, TypeVar

T = TypeVar('T')
ObjT = TypeVar('ObjT', bound='object')

__all__: Tuple[str, ...] = ('parse_time', 'to_json', 'to_string', 'copy_doc', 'simple_repr')


try:
    import orjson

    _has_orjson: bool = True
except ImportError:
    _has_orjson: bool = False
    import json

if _has_orjson:

    def to_json(string: str) -> Dict[Any, Any]:
        return orjson.loads(string)

    def to_string(data: Dict[Any, Any]) -> str:
        return orjson.dumps(data).decode('utf-8')

else:

    def to_json(string: str) -> Dict[Any, Any]:
        return json.loads(string)

    def to_string(data: Dict[Any, Any]) -> str:
        return json.dumps(data)


def parse_time(time_strp: str) -> datetime.datetime:
    """Parses the given tixte time string into a datetime object.

    Parameters
    ----------
    time_strp: :class:`str`
        The time string to parse.

    Returns
    -------
    :class:`datetime.datetime`
        The parsed datetime object.
    """
    return datetime.datetime.strptime(time_strp, '%Y-%m-%dT%H:%M:%S.%fZ')


def copy_doc(copy_from: Any) -> Callable[[T], T]:
    """Copy the documentation from the given object to the decorated function.

    .. code-block:: python3

        @copy_doc(MyObject)
        async def foo():
            pass

    Parameters
    ----------
    copy_from: Any
        The object to copy the documentation from.

    Returns
    -------
    Callable[..., Any]
        A wrapped callable that copies the documentation from the given object.
    """

    def wrapped(copy_to: T) -> T:
        copy_to.__doc__ = copy_from.__doc__
        return copy_to

    return wrapped


def simple_repr(cls: Type[ObjT]) -> Type[ObjT]:
    """Creates a simple repr for the given class.

    .. code-block:: python3

        @simple_repr
        class MyObject:
            __slots__ = ('id', 'name')

    Parameters
    ----------
    *attrs: :class:`str`
        The attributes to include in the repr.
    """
    cls_slots: Optional[Iterable[str]] = getattr(cls, '__slots__', None)

    def __repr__(self: ObjT) -> str:
        if not cls_slots:
            return f'<{cls.__name__}>'

        return f'<{cls.__name__} {" ".join(f"{attr}={getattr(self, attr)!r}" for attr in cls_slots if not attr.startswith("_"))}>'

    setattr(cls, '__repr__', __repr__)

    return cls
