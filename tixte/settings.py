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
import enum


from typing import TYPE_CHECKING, Optional, Tuple

from .utils import simple_repr
from .abc import Object

if TYPE_CHECKING:
    from types.settings import Settings as SettingsPayload

    from .state import State

__all__: Tuple[str, ...] = ('SharedFilesState', 'Settings', 'PartialSettings')


class SharedFilesState(enum.Enum):
    off = 3
    on = 1


class PartialSettings(Object):
    """Represents a partial version of your Tixte account settings.

    This has no knowledge of your current settings, but allows you to edit your settings
    and obtain a new :class:`Settings` object.
    """

    __slots__: Tuple[str, ...] = ('_state',)

    def __init__(self, state: State) -> None:
        self._state: State = state

    async def edit(
        self,
        *,
        promotional_emails: Optional[bool] = None,
        shared_file_emails: Optional[bool] = None,
        new_login_emails: Optional[bool] = None,
        allow_shared_files: Optional[SharedFilesState] = None,
        addable: Optional[bool] = None,
    ) -> Settings:
        """|coro|

        Edit your account settings and return a new :class:`Settings` object. Note that
        this does not make an effort to edit the current object, but rather returns a new one.

        Parameters
        ----------
        promotional_emails: Optional[:class:`bool`]
            Denotes whether or not your account will receive promotional emails.
        shared_file_emails: Optional[:class:`bool`]
            Denotes whether or not your account will receive emails when a file is shared with you.
        new_login_emails: Optional[:class:`bool`]
            Denotes whether or not your account will receive emails when a new login is detected.
        allowed_shared_files: Optional[:class:`SharedFilesState`]
            Denotes whether or not your account will allow files to be shared with you.
        addable: Optional[:class:`bool`]
            This field is not known at this time. It is either for allowing other users to add you as a friend or
            allowing other users to add you to another file, but it is unclear which one it is.

        Returns
        -------
        :class:`Settings`
            The new settings object.
        """
        data = await self._state.http.edit_settings(
            promotional=promotional_emails,
            shared_file=shared_file_emails,
            addable=addable,
            new_login=new_login_emails,
            shareable=allow_shared_files and allow_shared_files.value,
        )

        return Settings(state=self._state, data=data)


@simple_repr
class Settings(PartialSettings):
    """Represents your Tixte account settings.

    This inherits from :class:`PartialSettings`.

    Attributes
    ----------
    promotional_emails: :class:`bool`
        Denotes whether or not your account will receive promotional emails.
    shared_file_emails: :class:`bool`
        Denotes whether or not your account will receive emails when a file is shared with you.
    new_login_emails: :class:`bool`
        Denotes whether or not your account will receive emails when a new login is detected.
        This defaults to ``True`` when you create a new account on Tixte.
    allow_shared_files: :class:`SharedFilesState`
        Denotes whether or not your account will allow files to be shared with you.
    addable: :class:`bool`
        This field is not known at this time. It is either for allowing other users to add you as a friend or
        allowing other users to add you to another file, but it is unclear which one it is.
    """

    def __init__(self, *, state: State, data: SettingsPayload) -> None:
        self._state: State = state

        self.promotional_emails: bool = data['emails']['promotional']
        self.shared_file_emails: bool = data['emails']['shared_file']
        self.new_login_emails: bool = data['emails']['new_login']

        self.allow_shared_files: SharedFilesState = SharedFilesState(data['privacy']['shareable'])
        self.addable: bool = data['privacy']['addable']
