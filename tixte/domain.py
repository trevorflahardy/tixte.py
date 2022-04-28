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

from typing import TYPE_CHECKING, Any, Optional, Tuple, Dict
from .user import User
from .abc import Object

if TYPE_CHECKING:
    from .state import State

__all__: Tuple[str, ...] = ('Domain',)


class Domain(Object):
    """
    The class that represents a domain.
    
    .. container:: operations

        .. describe:: repr(x)

            Returns a string representation of the domain object.

    Attributes
    ---------
    url: :class:`str`
        The url of the domain.
    uploads: :class:`int`
        The total amount of uploads on the domain.
    owner_id: :class:`str`
        The id of the owner of the domain.
    """

    __slots__: Tuple[str, ...] = ('url', 'uploads', '_state', 'owner_id')

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        self._state: State = state

        self.url: str = data['name']
        self.uploads: int = data['uploads']
        self.owner_id: str = data['owner']

    def __repr__(self) -> str:
        return '<Domain url={0.url} uploads={0.uploads}>'.format(self)

    @property
    def owner(self) -> Optional[User]:
        """Optional[:class:`User`]: The owner of the domain, ``None`` if not cached."""
        return self._state.get_user(self.owner_id)

    async def fetch_owner(self) -> User:
        """|coro|

        A coroutine used to fetch the owner of the domain.

        Returns
        -------
        :class:`User`
            The owner of the domain.

        Raises
        ------
        Forbidden
            You do not have permission to fetch the user.
        NotFound
            The user with the given ID does not exist.
        HTTPException
            An HTTP error occurred.
        """
        data = await self._state.http.get_user(self.owner_id)
        return self._state.store_user(data)
