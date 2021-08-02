"""
The MIT License (MIT)
Copyright (c) 2015-present Rapptz
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

import datetime
from typing import (
    Any, 
    Dict,
    Optional, 
    Union,
    ClassVar
)

from .file import File

__all__ = (
    'User',
    'ClientUser',
)

class User:
    """
    The base User class.
    
    Attributes
    ----------
    id: :class:`str`
        The ID of the clientuser.
    username: :class:`str`
        The username of the clientuser.
    pro: :class:`bool`
        Whether or not the user has pro.
    beta: :class:`bool`
        Whether or not the user is in the beta.
    admin: :class:`bool`
        Whether or not the user is an admin.
    staff: :class:`bool`
        Whether or not the user is staff.
    avatar: Optional[:class:`str`]
        The user's avatar, if any.
    """
    
    __slots__ = ('_status', '_raw', 'id', 'username', 'avatar', 'pro', 'beta', 'admin', 'staff')
    
    def __init__(
        self,
        status: Any,
        data: Dict[str, Union[str, bool]]
    ) -> None:
        self._status = status
        self._raw = data
        
        self.id: str = data['id']
        self.username: str = data['username']
        self.avatar: Optional[str] = data['avatar']
        self.pro: bool = data['pro']
        self.beta: bool = data['beta']
        self.admin: bool = data['admin']
        self.staff: bool = data['staff']
        
    def __str__(self) -> str:
        return self.username
    
    def __eq__(self, o: object) -> bool:
        return self.id == o.id
    
    def __repr__(self) -> str:
        return f'<User {self.id} {self.username}>'
    
    async def save_avatar(
        self, 
    ) -> Optional[File]:
        if not self.avatar:
            return None
        return self._status.url_to_file(self.avatar)
        
        
        

class ClientUser(User):
    """
    The Clent's User profile. Because the client acts on behalf of your upload key, this fetches
    YOUR information.
    
    Attributes
    ----------
    id: :class:`str`
        The ID of the clientuser.
    username: :class:`str`
        The username of the clientuser.
    mfa_enabled: :class:`bool`
        Whether or not the user has MFA enabled.
    pro: :class:`bool`
        Whether or not the user has pro.
    beta: :class:`bool`
        Whether or not the user is in the beta.
    admin: :class:`bool`
        Whether or not the user is an admin.
    staff: :class:`bool`
        Whether or not the user is staff.
    email: :class:`str`
        The email registered to the user.
    email_verified: :class:`bool`
        If the email has been verified.
    phone: Optional[Any]
        The phone, if any, linked to the user account.
            ..note:
                I do not know if this is a str, I've never seen it.
                Please PR it if you have it filled in to get it updated.
    avatar: Optional[:class:`str`]
        The user's avatar, if any.
    upload_region: :class:`str`
        The user's upload region.
    raw_last_login: :class:`str`
        The user's raw last login.
    last_login: :class:`datetime.datetime`
        The user's raw_last_login formatted into datetime.
    """
    
    __slots__ = ('_raw', '_status', 'id', 'username', 'mfa_enabled', 'pro', 'beta', 'admin', 'staff', 'email', 'email_verified', 'phone', 'avatar', 'upload_region', 'raw_last_login')
    
    def __init__(
        self,
        status: Any,
        data: Dict[str, Union[str, bool]]
    ) -> None:
        super().__init__(status, data)
        
        self.mfa_enabled: bool = data['mfa_enabled']
        self.email: str = data['email']
        self.email_verified: bool = data['email_verified']
        self.phone: Optional[Any] = data['phone']
        self.upload_region: str = data['upload_region']
        self.raw_last_login = data['last_login']
        
        self._raw: ClassVar[Dict] = data
        self._status: Any = status
    
    @property
    def last_login(self) -> datetime.datetime:
        return datetime.datetime.strftime(self.raw_last_login, '%Y-%m-%dT%H:%M:%S.%fZ')

    def _dump_attrs_to_client(self, client):
        ignored = ('_raw', '_status')
        total = {}
        for slot in self.__slots__:
            if slot in ignored:
                continue
            value = getattr(self, slot)
            setattr(client, slot, value)
            total[slot] = value
        setattr(client, '_raw_user', total)
        
