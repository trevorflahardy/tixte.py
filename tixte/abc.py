"""
The MIT License (MIT)

Copyright (c) 2021-present NextChai

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from __future__ import annotations

from typing import Optional, Tuple, Type

from .utils import simple_repr

__all__: Tuple[str, ...] = ('Object', 'IDable')


@simple_repr
class Object(object):
    """The base object for all objects
    within the Tixte system. Every class inherits from this.
    """

    __slots__: Tuple[str, ...] = ()


@simple_repr
class IDable(Object):
    """Represents a Tixte :class:`~tixte.abc.Object` with an ID.
    This implements common comparison and hashing methods.

    This inherits :class:`~tixte.abc.Object`.

    .. container:: operations

        .. describe:: x == y

            Deteremines if two objects are equal.

        .. describe:: x != y

            Deteremines if two objects are not equal.

        .. describe:: hash(x)

            Returns the hash of the object.

    Parameters
    ----------
    id: :class:`str`
        The ID of the object.
    type_of: Optional[:class:`type`]
        The type of object this is. This is very useful
        if you're creating an IDable object that must be casted to another,
        and want the ``eq`` and ``ne`` methods to function normally.
        Defaults to :class:`IDable`.
    """

    __slots__: Tuple[str, ...] = ('id', 'type_of')

    def __init__(self, id: str, *, type_of: Optional[Type[IDable]] = None) -> None:
        self.id: str = id
        self.type_of: Type[IDable] = type_of or IDable

    def __eq__(self, __other: object) -> bool:
        if not isinstance(__other, self.type_of):
            return False

        return self.id == __other.id

    def __ne__(self, __other: object) -> bool:
        return not self.__eq__(__other)

    def __hash__(self) -> int:
        return hash(self.id)
