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
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Tuple,
)

from .file import File
from .abc import IDable

if TYPE_CHECKING:
    from .state import State

__all__: Tuple[str, ...] = (
    'User',
    'ClientUser',
)


class User(IDable):
    """
    The base User class.

    Attributes
    ----------
    id: :class:`str`
        The ID of the user.
    username: :class:`str`
        The username of the user.
    pro: :class:`bool`
        Whether the user is a pro.
    beta: :class:`bool`
        Whether or not the user is in the beta.
    admin: :class:`bool`
        Whether or not the user is an admin.
    staff: :class:`bool`
        Whether or not the user is staff.
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
        self.avatar: Optional[str] = data['avatar']
        self.beta: Optional[bool] = data.get('beta')
        self.admin: Optional[bool] = data.get('admin', None)
        self.staff: Optional[bool] = data.get('staff')
        self.pro: Optional[bool] = data.get('pro')

    def __str__(self) -> str:
        return self.username

    def __repr__(self) -> str:
        return '<User id={0.id} username={0.username} avatar={0.avatar} pro={0.pro} beta={0.beta} admin={0.admin} staff={0.staff}>'.format(
            self
        )

    async def save_avatar(self, *, filename: str) -> Optional[File]:
        """
        Save the user's avatar to a :class:`File` obj.
        Could return None if the user has not set an avatar.

        Returns
        -------
        Optional[:class:`File`]
        """
        if not self.avatar:
            return None

        return await self._state.http.url_to_file(url=self.avatar, filename=filename)


class ClientUser(User):
    """
    The Clent's User profile. This contains metadata specific to the user,
    such as their email address and phone number.
    
    This inherits from :class:`User`.

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
    """

    __slots__: Tuple[str, ...] = (
        'mfa_enabled',
        'email',
        'email_verified',
        'phone',
        'upload_region',
        '_last_login',
    )

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        super().__init__(state=state, data=data)

        self.mfa_enabled: bool = data['mfa_enabled']
        self.email: str = data['email']
        self.email_verified: bool = data['email_verified']
        self.phone: Optional[Any] = data['phone']
        self.upload_region: str = data['upload_region']
        self._last_login = data['last_login']

    def __repr__(self) -> str:
        return '<ClientUser id={0.id} username={0.username} avatar={0.avatar} pro={0.pro} beta={0.beta} admin={0.admin} staff={0.staff} email={0.email} email_verified={0.email_verified} phone={0.phone} upload_region={0.upload_region} mfa_enabled={0.mfa_enabled}>'.format(
            self
        )

    @property
    def last_login(self) -> datetime.datetime:
        """:class:`datetime.datetime`: The last time the user logged in."""
        return datetime.datetime.strptime(self._last_login, '%Y-%m-%dT%H:%M:%S.%fZ')
