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

from typing import TYPE_CHECKING, Any, Dict, Tuple

from .abc import IDable, Object

if TYPE_CHECKING:
    from .state import State

__all__: Tuple[str, ...] = ('PartialUpload', 'Upload', 'DeleteResponse')


class PartialUpload(IDable):
    """Represents a Partial Uploaded File. This can be used to delete an upload
    with only it's ID.

    This object can get obtained by calling :meth:`Client.get_partial_upload`.

    Attributes
    ----------
    id: :class:`str`
        The ID of the partial upload.
    """

    __slots__: Tuple[str, ...] = ('_state', 'id')

    def __init__(self, *, state: State, id: str) -> None:
        self._state: State = state
        self.id: str = id

    def __repr__(self) -> str:
        return '<PartialUpload id={0.id}>'.format(self)

    async def delete(self) -> DeleteResponse:
        """|coro|

        Delete the file from Tixte.

        Returns
        -------
        :class:`DeleteResponse`
            The response from Tixte with the status of the deletion.
        """
        data = await self._state.http.delete_file(self.id)
        return DeleteResponse(state=self._state, data=data)


class Upload(PartialUpload):
    """
    The base FileResponse obj you get back when uploading an image.

    Attributes
    ----------
    id: :class:`str`
        The ID of the file.
    filename: :class:`str`
        The filename of the file.
    extension: :class:`str`
        The file extension. For example ``.png`` or ``.jpg``.
    url: :class:`str`
        The URL for the newly uploaded image.
    direct_url: :class:`str`
        The Direct URL for the newly uploaded image.
    """

    __slots__: Tuple[str, ...] = ('_state', 'id', 'filename', 'extension', 'url', 'direct_url')

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        self._state: State = state

        self.id: str = data['id']
        self.filename: str = data['filename']
        self.extension: str = data['extension']
        self.url: str = data['url']
        self.direct_url: str = data['direct_url']

    def __repr__(self) -> str:
        return '<Upload id={0.id} filename={0.filename} extension={0.extension} url={0.url} direct_url={0.direct_url}>'.format(
            self
        )


class DeleteResponse(Object):
    """Represents the response from Tixte when deleting a file.

    Attributes
    ----------
    message: :class:`str`
        The message from Tixte with the status of the deletion.
    """

    __slots__: Tuple[str, ...] = (
        '_state',
        'message',
    )

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        self._state: State = state
        self.message: str = data['message']

    def __repr__(self) -> str:
        return '<DeleteResponse message={0.message}>'.format(self)
