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

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from .abc import Object
from .delete import DeleteResponse
from .user import User
from .utils import simple_repr

if TYPE_CHECKING:
    from .state import State

__all__: Tuple[str, ...] = ('Domain',)


@simple_repr
class Domain(Object):
    """
    The class that represents a domain.

    .. container:: operations

        .. describe:: repr(x)

            Returns a string representation of the domain object.

        .. describe:: x == y

            Deteremines if two domains are equal. This will compare using the url, upload count, and owner ID.
            If you are comparing two equal domains with different uploads, they will show as not equal.

        .. describe:: x != y

            Deteremines if two domains are not equal. This will compare using the url, upload count, and owner ID.
            If you are comparing two equal domains with different uploads, they will show as not equal.

        .. describe:: hash(x)

            Returns the hash of the domain.

        .. describe:: str(x)

            Returns the url of the domain.

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

    def __eq__(self, __o: Any) -> bool:
        return self.url == __o.url and self.uploads == __o.uploads and self.owner_id == __o.owner_id

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __hash__(self) -> int:
        return hash((self.url, self.uploads, self.owner_id))

    def __str__(self) -> str:
        return self.url

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

    async def delete(self) -> DeleteResponse:
        """|coro|

        Deletes the domain.

        Returns
        -------
        :class:`DeleteResponse`
            The response from the delete request. :attr:`DeleteResponse.extra` will contain a ``domain``
            key.
        """
        data = await self._state.http.delete_domain(self.url)
        self._state.remove_domain(self.url)
        return DeleteResponse(state=self._state, data=data)
