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
from collections.abc import Sequence

import io
import sys
import aiohttp
import asyncio
import logging
from typing import (
    ClassVar,
    Any,
    Coroutine,
    Optional,
    Dict,
    Tuple,
    Union,
    TypeVar,
    Callable,
    List,
)
from typing_extensions import TypeAlias

from .errors import Forbidden, NotFound, TixteServerError, HTTPException
from .file import File
from . import __version__
from .utils import to_json

__all__: Tuple[str, ...] = ('Route', 'HTTP')

T = TypeVar('T')
Response: TypeAlias = Coroutine[Any, Any, T]

log = logging.getLogger(__name__)


class Route:
    """
    Route for the lib. Similar to how discord.py (https://github.com/Rapptz/discord.py/tree/master) does it,
    we'll use this for organizing any API calls.

    Parameters
    ----------
    method: :class:`str`
        The method you want to use.
    path: :class:`str`
        The additional path you want to use
    **parameters: Any
        Any params you want to add onto the url.
    """

    __slots__: Tuple[str, ...] = ('method', 'path', 'url')

    BASE: ClassVar[str] = 'https://api.tixte.com/v1'

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        if parameters:
            try:
                path = path.format(**parameters)
            except IndexError:
                pass

        self.path: str = path
        self.url: str = self.BASE + self.path
        self.method: str = method


class ExpandableRoute(Route):
    """An expanded route that allows for 3rd party urls to be passed to the
    :meth:`HTTP.request` method.
    """

    __slots__: Tuple[str, ...] = (
        'url',
        'method',
    )

    def __init__(self, method: str, url: str, **parameters: Any) -> None:
        if parameters:
            try:
                url = url.format(**parameters)
            except IndexError:
                pass

        self.url: str = url
        self.method: str = method


class HTTP:
    __slots__: Tuple[str, ...] = (
        'session',
        'master_key',
        'domain',
        'user_agent',
        'session_lock',
        'dispatch',
    )

    # Credit to:
    # https://github.com/Rapptz/discord.py/blob/master/discord/http.py#L163
    REQUEST_LOG: ClassVar[str] = '{method} {url} with {json} has returned {status}'

    def __init__(
        self,
        *,
        master_key: str,
        domain: str,
        dispatch: Callable[..., List[asyncio.Task[Any]]],
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.master_key: str = master_key
        self.domain: str = domain

        self.dispatch: Callable[..., List[asyncio.Task[Any]]] = dispatch

        self.session: Optional[aiohttp.ClientSession] = session
        self.session_lock: asyncio.Lock = asyncio.Lock()

        user_agent = (
            'TixteClient (https://github.com/NextChai/Tixte {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        )
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def create_client_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def _json_or_text(
        self, response: aiohttp.ClientResponse
    ) -> Union[Dict[str, Any], str, bytes]:
        try:
            text = await response.text()
        except UnicodeDecodeError:  # This is bytes
            return await response.read()

        if response.headers.get('Content-Type') == 'application/json; charset=utf-8':
            return to_json(text)

        return text

    async def request(
        self,
        route: Route,
        files: Optional[Sequence[File]] = None,
        **kwargs: Any,
    ) -> Any:
        if self.session is None:
            raise RuntimeError('No session available')

        method = route.method
        url = route.url

        headers = {'User-Agent': self.user_agent}

        if not isinstance(route, ExpandableRoute):
            headers['Authorization'] = self.master_key

        kwargs['headers'] = headers

        if files is not None:
            data = aiohttp.FormData()
            for index, file in enumerate(files):
                data.add_field(
                    f'file{index}',
                    file.fp,
                    filename=file.filename,
                    content_type='application/octet-stream',
                )

            kwargs['data'] = data

        response: Optional[aiohttp.ClientResponse] = None
        async with self.session_lock:
            for tries in range(5):
                async with self.session.request(method, url, **kwargs) as response:
                    self.dispatch('request', response)

                    data = await self._json_or_text(response)

                    if 300 > response.status >= 200:  # Everything is ok
                        fmt_data = (
                            data
                            if not isinstance(data, bytes)
                            else f'<binary data with len {len(data)}>'
                        )
                        log.debug(
                            self.REQUEST_LOG.format(
                                method=method,
                                url=url,
                                json=fmt_data,
                                status=response.status,
                            )
                        )

                        if files is not None:
                            for file in files:
                                file.close()

                        if isinstance(data, dict) and (inner := data.get('data')):
                            return inner

                        return data

                    if response.status == 429:  # We're rate limited
                        headers = response.headers
                        retry_after: float = float(
                            headers['x-ratelimit-reset']
                        )  # Retry the status after this amount of time
                        if retry_after == 0 and not headers.get('x-ratelimit-remaining'):
                            retry_after: float = float(headers['Retry-After'])

                        fmt = f'We are being rate limited! Trying again in {retry_after} seconds.'
                        log.warning(fmt)

                        await asyncio.sleep(retry_after)  # Sleep until no ratelimit :ok_hand:
                        continue

                    if response.status in {
                        500,
                        502,
                        504,
                    }:  # Taken from d.py yayy
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # Anything else here is going to raise, let's close all of the files
                    if files is not None:
                        for file in files:
                            file.close()

                    if response.status == 403:
                        raise Forbidden(response, data)
                    elif response.status == 404:
                        raise NotFound(response, data)
                    elif response.status >= 500:
                        raise TixteServerError(response, data)
                    else:
                        raise HTTPException(response, data)

        # We've run into a problem, let's close all of the files
        if files is not None:
            for file in files:
                file.close()

        if response is not None:
            if response.status >= 500:
                raise TixteServerError(response, data)  # type: ignore # The prereq is that response != None so data is not unbound

            raise HTTPException(response, data)  # type: ignore # Here as well

        raise RuntimeError('Unreachable code in HTTP handling')

    def upload_file(self, file: File) -> Response[Dict[Any, Any]]:
        r = Route('POST', '/upload?domain={domain}', domain=self.domain)
        return self.request(r, files=[file])

    def delete_file(self, upload_id: str) -> Response[Dict[Any, Any]]:
        r = Route('DELETE', '/users/@me/uploads/{upload_id}', upload_id=upload_id)
        return self.request(r)

    def get_client_user(self) -> Response[Dict[Any, Any]]:
        r = Route('GET', '/users/@me')
        return self.request(r)

    def get_user(self, user_id: str) -> Response[Dict[Any, Any]]:
        r = Route('GET', '/users/{user_id}', user_id=user_id)
        return self.request(r)

    def get_domains(self) -> Response[Dict[Any, Any]]:
        r = Route('GET', '/users/@me/domains')
        return self.request(r)

    def get_config(self) -> Response[Dict[Any, Any]]:
        r = Route('GET', '/users/@me/config')
        return self.request(r)

    def get_total_upload_size(self) -> Response[Dict[Any, Any]]:
        r = Route('GET', '/users/@me/uploads/size')
        return self.request(r)

    async def url_to_file(self, *, url: str, filename: str) -> File:
        data = await self.request(ExpandableRoute('GET', url))
        bytes_io = io.BytesIO(data)
        bytes_io.seek(0)
        return File(bytes_io, filename=filename)
