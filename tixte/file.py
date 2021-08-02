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

import os
import io

from typing import Dict, Optional, Union


__all__ = (
    'File',
    'FileResponse'
)

class File:
    r"""A parameters object used to upload to the tixte API.
    
    Attributes
    -----------
    fp: Union[:class:`os.PathLike`, :class:`io.BufferedIOBase`]
        A file-like object opened in binary mode and read mode
        or a filename representing a file in the hard drive to
        open.
        .. note::
            If the file-like object passed is opened via ``open`` then the
            modes 'rb' should be used.
            To pass binary data, consider usage of ``io.BytesIO``.
    filename: Optional[:class:`str`]
        The filename to display when uploading to Discord.
        If this is not given then it defaults to ``fp.name`` or if ``fp`` is
        a string then the ``filename`` will default to the string given.
    """

    __slots__ = ('fp', 'filename', 'spoiler', '_original_pos', '_owner', '_closer')

    def __init__(
        self,
        fp: Union[str, bytes, os.PathLike, io.BufferedIOBase],
        filename: Optional[str] = None
    ):
        if isinstance(fp, io.IOBase):
            if not (fp.seekable() and fp.readable()):
                raise ValueError(f'File buffer {fp!r} must be seekable and readable')
            self.fp = fp
            self._original_pos = fp.tell()
            self._owner = False
        else:
            self.fp = open(fp, 'rb')
            self._original_pos = 0
            self._owner = True

        # aiohttp only uses two methods from IOBase
        # read and close, since I want to control when the files
        # close, I need to stub it so it doesn't close unless
        # I tell it to
        self._closer = self.fp.close
        self.fp.close = lambda: None

        if filename is None:
            if isinstance(fp, str):
                _, self.filename = os.path.split(fp)
            else:
                self.filename = getattr(fp, 'name', None)
        else:
            self.filename = filename
            
    def reset(self, *, seek: Union[int, bool] = True) -> None:
        # The `seek` parameter is needed because
        # the retry-loop is iterated over multiple times
        # starting from 0, as an implementation quirk
        # the resetting must be done at the beginning
        # before a request is done, since the first index
        # is 0, and thus false, then this prevents an
        # unnecessary seek since it's the first request
        # done.
        if seek:
            self.fp.seek(self._original_pos)

    def close(self) -> None:
        self.fp.close = self._closer
        if self._owner:
            self._closer()
            
class FileResponse:
    """
    The base FileResponse obj you get back when uploading an image.
    
    Attributes
    ----------
    id: :class:`str`
        The ID of the file.
    filename: :class:`str`
        The filename of the file.
    extension: :class:`str`
        The file extension. Ex: .png
    url: :class:`str`
        The URL for the newly uploaded image.
    direct_url: :class:`str`
        The Direct URL for the newly uploaded image.

    Methods
    -------
    delete:
        Delete the file.
    """
    
    __slots__ = ('_status', '_raw', 'id', 'filename', 'extension', 'url', 'direct_url')
    
    def __init__(
        self,
        status,
        data: Dict
    ) -> None:
        self._status = status
        
        self._raw = data
        
        self.id: str = data['id']
        self.filename: str = data['filename']
        self.extension: str = data['extension']
        self.url: str = data['url']
        self.direct_url: str = data['direct_url']
        
    def __eq__(self, o: object) -> bool:
        return self.id == o.id
    
    def __str__(self) -> str:
        return self.direct_url

    async def delete(self) -> None:
        return await self._status.delete_file(self.id)