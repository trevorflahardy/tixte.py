import datetime
from typing import (
    Any, 
    Dict,
    Optional, 
    Union,
    ClassVar
)

from .errors import NotImplementedError

__all__ = (
    'ClientUser',
    'User'
)

class ClientUser:
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
        self._raw: ClassVar[Dict] = data
        self._status: Any = status
        
        self.id: str = data['id']
        self.username: str = data['username']
        self.mfa_enabled: bool = data['mfa_enabled']
        self.pro: bool = data['pro']
        self.beta: bool = data['beta']
        self.admin: bool = data['admin']
        self.staff: bool = data['staff']
        self.email: str = data['email']
        self.email_verified: bool = data['email_verified']
        self.phone: Optional[Any] = data['phone']
        self.avatar: Optional[str] = data['avatar']
        self.upload_region: str = data['upload_region']
        self.raw_last_login = data['last_login']
    
    @property
    def last_login(self) -> datetime.datetime:
        return datetime.datetime.strftime(self.raw_last_login, '%Y-%m-%dT%H:%M:%S.%fZ')

    def _dump_attrs_to_client(self, client):
        ignored = ('_raw', '_status')
        for slot in self.__slots__:
            if slot in ignored:
                continue
            value = getattr(self, slot)
            setattr(client, slot, value)
    
class User:
    def __init__(
        self,
        status: Any,
        data: Dict[str, Union[str, bool]]
    ) -> None:
        self._status = status
        self._raw = data