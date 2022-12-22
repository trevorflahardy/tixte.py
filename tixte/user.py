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

import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from .abc import IDable
from .enums import Premium, Region
from .file import File
from .utils import parse_time, simple_repr

if TYPE_CHECKING:
    from .state import State

__all__: Tuple[str, ...] = (
    'User',
    'ClientUser',
)


@simple_repr
class User(IDable):
    """This class holds all attributes and methods that are unique to users.

    .. container:: operations

        .. describe:: repr(x)

            Returns a string representation of the User.

        .. describe:: str(x)

            Returns the username of the user.

        .. describe:: x == y

            Deteremines if two Users are equal.

        .. describe:: x != y

            Deteremines if two Users are not equal.

        .. describe:: hash(x)

            Returns the hash of the User.

    Attributes
    ----------
    id: :class:`str`
        The ID of the user.
    username: :class:`str`
        The username of the user.
    avatar: Optional[:class:`str`]
        The user's avatar, if any.
    """

    __slots__: Tuple[str, ...] = (
        '_state',
        'id',
        'username',
        'avatar',
        'pro',
        'beta',
        'admin',
        'staff',
    )

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        self._state: State = state

        self.id: str = data['id']
        self.username: str = data['username']
        self.avatar: Optional[str] = data.get('avatar')

    def __str__(self) -> str:
        return self.username

    async def save_avatar(self, *, filename: str) -> Optional[File]:
        """|coro|

        Save the user's avatar to a :class:`File` obj.
        Could return ``None`` if the user has not set an avatar.

        Returns
        -------
        Optional[:class:`File`]
            The file object, or ``None`` if the :class:`User` has not set an avatar.
        """
        if not self.avatar:
            return None

        return await self._state.http.url_to_file(url=self.avatar, filename=filename)


@simple_repr
class ClientUser(User):
    """
    The Clent's User profile. This contains metadata specific to the user,
    such as their email address and phone number.

    This inherits from :class:`User`.

    .. container:: operations

        .. describe:: repr(x)

            Returns a string representation of the ClientUser.

        .. describe:: str(x)

            Returns the username of the ClientUser.

        .. describe:: x == y

            Deteremines if two ClientUsers are equal.

        .. describe:: x != y

            Deteremines if two ClientUsers are not equal.

        .. describe:: hash(x)

            Returns the hash of the ClientUser.

    Attributes
    ----------
    mfa_enabled: :class:`bool`
        Whether or not the user has MFA enabled.
    email: :class:`str`
        The email registered to the user.
    email_verified: :class:`bool`
        If the email has been verified.
    phone: Optional[Any]
        The phone, if any, linked to the user account.
    upload_region: :class:`str`
        The user's upload region.
    premium: :class:`Premium`
        Your current premium status.
    """

    __slots__: Tuple[str, ...] = (
        'mfa_enabled',
        'email',
        'email_verified',
        'phone',
        'upload_region',
        '_last_login',
        'premium_tier',
    ) + User.__slots__

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        super().__init__(state=state, data=data)

        self.mfa_enabled: bool = data['mfa_enabled']
        self.premium_tier: Premium = Premium(data['premium_tier'])
        self.email: str = data['email']
        self.email_verified: bool = data['email_verified']
        self.phone: Optional[Any] = data['phone']
        self.upload_region: Region = Region(data['upload_region'])
        self._last_login = data['last_login']

    @property
    def last_login(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The last time the user logged in."""
        return parse_time(self._last_login)
