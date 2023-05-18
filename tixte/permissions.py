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

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union, overload

from .abc import Object
from .enums import UploadPermissionLevel

if TYPE_CHECKING:
    from .state import State
    from .upload import PartialUpload, Upload
    from .user import User


@overload
def _parse_permissions(state: State, parser: None) -> None:
    ...


@overload
def _parse_permissions(state: State, parser: List[Dict[str, Any]]) -> Dict[User, UploadPermissionLevel]:
    ...


def _parse_permissions(state: State, parser: Optional[List[Dict[str, Any]]]) -> Optional[Dict[User, UploadPermissionLevel]]:
    if not parser:
        return None

    data: Dict[User, UploadPermissionLevel] = {}

    for entry in parser:
        data[state.store_user(entry['user'])] = UploadPermissionLevel(entry['access_level'])

    return data


class Permissions(Object):
    """Represents the Permissions of a :class:`PartialUpload` or :class:`Upload`.

    Please note that if this stems from a :class:`PartialUpload`, then the :meth:`get` method will
    be ``None`` 100% of the time unless you call :meth:`fetch`.

    Attributes
    ----------
    upload: Union[:class:`PartialUpload`, :class:`Upload`]
        The upload that these permissions are for.
    """

    __slots__: Tuple[str, ...] = ('_state', 'upload', '_permissions')

    def __init__(
        self,
        *,
        state: State,
        upload: Union[PartialUpload, Upload],
        permission_mapping: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self._state: State = state
        self.upload: Union[PartialUpload, Upload] = upload

        self._permissions: Optional[Dict[User, UploadPermissionLevel]] = _parse_permissions(state, permission_mapping)

    def get(self) -> Optional[Dict[User, UploadPermissionLevel]]:
        """Get the permissions of the upload.

        Please note this can be incomplete if you haven't called :meth:`fetch`.

        Returns
        -------
        Optional[Mapping[:class:`User`, :class:`UploadPermissionLevel`]]
            A mapping of users to their permissions. If this is ``None``, you can fetch the permissions by calling
            :meth:`fetch`.
        """
        return self._permissions

    async def fetch(self) -> Dict[User, UploadPermissionLevel]:
        """|coro|

        Fetch the permissions for the upload. This is a helpful method if :meth:`get` returns ``None``
        as it will fill the attribute.

        Returns
        -------
        Mapping[:class:`User`, :class:`UploadPermissionLevel`]
            A mapping of users to their permissions.
        """
        data = await self._state.http.get_upload_permissions(self.upload.id)
        self._permissions = permissions = _parse_permissions(self._state, data)
        return permissions

    async def add(self, user: User, /, *, level: UploadPermissionLevel, message: Optional[str] = None) -> User:
        """|coro|

        Add a user to this upload\'s permissions. For example, if this is a private upload you can grant
        this user access to view the upload.

        Parameters
        ----------
        user: :class:`User`
            The user to add to the permissions.
        level: :class:`UploadPermissionLevel`
            The permission level to grant the user. Note that granting the user :attr:`UploadPermissionLevel.owner` will
            transfer ownership to the user and you will no longer be able to edit the upload as you won't own it.
        message: Optional[:class:`str`]
            An optional message to pass along to the user.

        Returns
        -------
        :class:`User`
            The user that was added to the permissions.

        Raises
        ------
        HTTPException
            This user is already in the permissions.
        """
        result = await self._state.http.add_upload_permissions(
            upload_id=self.upload.id, user_id=user.id, permission_level=level.value, message=message
        )
        user = self._state.store_user(result['user'])

        if self._permissions:
            self._permissions[user] = level

        return user

    async def remove(self, user: User, /) -> None:
        """|coro|

        Remove the current permissions of a user. For example, if this is a private upload you can revoke
        the user's access to view the upload.

        Parameters
        ----------
        user: :class:`User`
            The user to remove from the permissions.

        Raises
        ------
        NotFound
            This user is not in the permissions so you can not remove them.
        """
        await self._state.http.remove_upload_permissions(upload_id=self.upload.id, user_id=user.id)

        if self._permissions:
            self._permissions.pop(user, None)

    async def edit(self, user: User, /, *, level: UploadPermissionLevel) -> User:
        """|coro|

        Edit the permissions of a user. For example, if this is a private upload you can edit
        the user's access to view the upload.

        .. note::

            Granting the user :attr:`UploadPermissionLevel.owner` will transfer ownership to the user and you will no longer
            be able to manage this upload.

        Parameters
        ----------
        user: :class:`User`
            The user to edit the permissions of.
        level: :class:`UploadPermissionLevel`
            The permission level to grant the user.

        Returns
        -------
        :class:`User`
            The user that was edited.
        """
        result = await self._state.http.edit_upload_permissions(
            upload_id=self.upload.id, user_id=user.id, permission_level=level.value
        )
        user = self._state.store_user(result['user'])

        if self._permissions:
            self._permissions[user] = level

        return user
