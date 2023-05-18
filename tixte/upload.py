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

from .abc import IDable
from .delete import DeleteResponse
from .enums import Region, UploadType
from .permissions import Permissions
from .utils import parse_time, simple_repr

if TYPE_CHECKING:
    import datetime

    from .domain import Domain
    from .file import File
    from .state import State

__all__: Tuple[str, ...] = ('PartialUpload', 'Upload')


@simple_repr
class PartialUpload(IDable):
    """Represents a Partial Uploaded File. This can be used to delete an upload
    with only it's ID.

    This object can get obtained by calling :meth:`Client.get_partial_upload`.

    .. container:: operations

        .. describe:: repr(x)

            Returns a string representation of the partial upload.

        .. describe:: x == y

            Deteremines if two partial uploads are equal.

        .. describe:: x != y

            Deteremines if two partial uploads are not equal.

        .. describe:: hash(x)

            Returns the hash of the partial upload.

    Attributes
    ----------
    id: :class:`str`
        The ID of the partial upload.
    """

    __slots__: Tuple[str, ...] = ('_state', 'id', 'permissions')

    def __init__(self, *, state: State, id: str) -> None:
        self._state: State = state
        self.id: str = id
        self.permissions: Permissions = Permissions(state=self._state, upload=self)

    async def delete(self) -> DeleteResponse:
        """|coro|

        Delete the file from Tixte.

        Returns
        -------
        :class:`DeleteResponse`
            The response from Tixte with the status of the deletion.
        """
        data = await self._state.http.delete_upload(self.id)
        return DeleteResponse(state=self._state, data=data)

    # NOTE: Tixte took this out of their API
    # async def fetch(self) -> Upload:
    #     """|coro|
    #
    #     Fetch the upload and return it.
    #
    #     Returns
    #     -------
    #     :class:`Upload`
    #         The upload that was requested.
    #
    #     Raises
    #     ------
    #     Forbidden
    #         You do not have permission to fetch this upload.
    #     HTTPException
    #         An HTTP exception has occurred.
    #     """
    #     data = await self._state.http.get_upload(self.id)
    #     return Upload(state=self._state, data=data)


@simple_repr
class Upload(PartialUpload):
    """The class that represents the response from Tixte when uploading a file.

    This inherits :class:`PartialUpload`.

    .. container:: operations

        .. describe:: repr(x)

            Returns a string representation of the upload.

        .. describe:: x == y

            Deteremines if two uploads are equal.

        .. describe:: x != y

            Deteremines if two uploads are not equal.

        .. describe:: hash(x)

            Returns the hash of the upload.

    Attributes
    ----------
    id: :class:`str`
        The ID of the file.
    name: :class:`str`
        The name of the file.
    filename: :class:`str`
        The filename of the file. This is the combined name and extension of the file.
    extension: :class:`str`
        The file extension. For example ``.png`` or ``.jpg``.
    url: :class:`str`
        The URL for the newly uploaded image.
    direct_url: :class:`str`
        The Direct URL for the newly uploaded image.
    permissions: Dict[:class:`User`, :class:`UploadPermissionLevel`]
        A mapping of users to their permission levels.
    type: :class:`UploadType`
        The type of upload.
    """

    __slots__: Tuple[str, ...] = (
        '_state',
        'id',
        'name',
        'extension',
        'url',
        'direct_url',
        'domain_url',
        'region',
        'expiration',
        'permissions',
        'type',
        'filename',
    )

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        self._state: State = state

        self.id: str = data['id']
        self.name: str = data['name']
        self.region: Optional[Region] = Region(region) if (region := data.get('region')) else None
        self.permissions: Permissions = Permissions(
            state=self._state, upload=self, permission_mapping=data.get('permissions', None)
        )
        self.domain_url: str = data['domain']
        self.type: UploadType = UploadType(data['type'])
        self.filename: str = data['filename']

        self.expiration: Optional[datetime.datetime] = (expiration := data['expiration']) and parse_time(expiration)
        self.extension: str = data['extension']
        self.url: str = data.get('url') or f'https://{self.domain_url}/{self.name}.{self.extension}'
        self.direct_url: Optional[str] = data.get('direct_url')

    @property
    def domain(self) -> Optional[Domain]:
        """Optional[:class:`Domain`]: The domain that the upload is located in."""
        return self._state.get_domain(self.domain_url)

    async def to_file(self) -> File:
        """|coro|

        A coroutine to turn this :class:`Upload` to a :class:`File` object.

        Returns
        -------
        :class:`File`
            The file object created from downloading this upload's image.
        """
        return await self._state.http.url_to_file(url=self.url, filename=self.filename)

    async def fetch_domain(self) -> Domain:
        """|coro|

        A method used to fetch the domain this upload is registered under. Consider using :attr:`domain`
        first before calling this.

        Returns
        --------
        :class:`Domain`
            The domain that this upload is registered under.

        Raises
        ------
        Forbidden
            You do not have permission to fetch this domain.
        HTTPException
            An HTTP exception has occurred.
        """
        domains = await self._state.http.get_domains()
        for domain in domains:
            if domain.url == self.domain_url:
                return domain

        raise RuntimeError(f'Domain {self.domain_url} not found.')
