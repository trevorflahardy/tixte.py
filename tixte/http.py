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

import asyncio
import io
import logging
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    TypedDict,
    Union,
)
import aiohttp
from typing_extensions import TypeAlias

from . import __version__
from .errors import *
from .file import File
from .utils import to_json, to_string
from .types.base import Response as ResponseDict, TypedDictT

if TYPE_CHECKING:
    from .domain import Domain

    from .types import user, error, upload, base


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
        dispatch: Callable[..., None],
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.master_key: str = master_key
        self.domain: str = domain

        self.dispatch: Callable[..., None] = dispatch

        self.session: Optional[aiohttp.ClientSession] = session
        self.session_lock: asyncio.Lock = asyncio.Lock()

        user_agent = 'TixteClient (https://github.com/NextChai/Tixte {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def create_client_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def _json_or_text(self, response: aiohttp.ClientResponse) -> Union[ResponseDict[Any], str]:
        text = await response.text(encoding='utf-8')

        if response.headers.get('Content-Type') == 'application/json; charset=utf-8':
            return to_json(text)

        return text

    def _resolve_data(self, json_or_text: Union[str, ResponseDict[TypedDictT]]) -> Union[str, error.Error, TypedDictT]:
        if isinstance(json_or_text, str):
            return json_or_text

        # We know this to be the response dict, so we can narrow it down
        if json_or_text['success'] is False:
            error = json_or_text.get('error')
            if error is None:
                # This should never happen, but if it does we need to alert the user they need
                # to open an issue on the GitHub repo
                raise TixteException('Unknown error has occured. Please open an issue on the GitHub repo.')

            return error

        data: Optional[TypedDictT] = json_or_text.get('data')
        if data is None:
            # Similar to above, this should not happen under any circumstances.. if it does happen
            # it is a Tixte issue.
            raise TixteException('Unknown error has occured. Please open an issue on the GitHub repo.')

        return data

    async def request(
        self,
        route: Route,
        files: Optional[Sequence[File]] = None,
        **kwargs: Any,
    ) -> Any:
        if self.session is None:
            self.session = aiohttp.ClientSession()

        method = route.method
        url = route.url

        headers = {
            'User-Agent': self.user_agent,
            'Authorization': self.master_key,
            #'Content-Type': 'application/json',
        }
        kwargs['headers'] = headers

        # Check for JSON data
        if 'json' in kwargs:
            kwargs['data'] = to_string(kwargs.pop('json'))

        if files is not None:
            form_data = aiohttp.FormData()

            # Need to append the JSON data to the given form data
            if 'data' in kwargs:
                form_data.add_field('payload_json', kwargs.pop('data'))
                log.debug('Added payload_json to form data')

            for index, file in enumerate(files):
                form_data.add_field(
                    name=f'file[{index}]',
                    value=file.fp,
                    filename=file.filename,
                )

            kwargs['data'] = form_data

        response: Optional[aiohttp.ClientResponse] = None
        resolved_data: Optional[Union[str, TypedDict, error.Error]] = None
        async with self.session_lock:
            for tries in range(5):
                async with self.session.request(method, url, **kwargs) as response:
                    self.dispatch('request', response)

                    data = await self._json_or_text(response)

                    log.debug(
                        self.REQUEST_LOG.format(
                            method=method,
                            url=url,
                            json=data,
                            status=response.status,
                        )
                    )

                    # Let's resolve this data before parsing
                    resolved_data = self._resolve_data(data)

                    if 300 > response.status >= 200:  # Everything is ok
                        if files is not None:
                            for file in files:
                                file.close()

                        return resolved_data

                    if response.status == 429:
                        # We've been rate limited here, for one reason or another. Let's get the retry after value
                        # and then try again.
                        headers = response.headers
                        retry_after: float = float(headers['x-ratelimit-reset'])

                        if retry_after == 0 and not headers.get('x-ratelimit-remaining'):
                            retry_after: float = float(headers['Retry-After'])

                        fmt = f'We are being rate limited! Trying again in {retry_after} seconds.'
                        log.warning(fmt)

                        await asyncio.sleep(retry_after)  # Sleep until no ratelimit
                        continue

                    # One of server error, bad gateway, or gateway timeout, we can try again
                    if response.status in {
                        500,
                        502,
                        504,
                    }:
                        await asyncio.sleep(1 + tries * 2)
                        continue

                    # All these are exceptions, which which will all raise. We can close
                    # ay open files and narrow the error down.
                    if files is not None:
                        for file in files:
                            file.close()

                    if response.status == 402:
                        raise PaymentRequired(response, resolved_data)
                    if response.status == 403:
                        raise Forbidden(response, resolved_data)
                    elif response.status == 404:
                        raise NotFound(response, resolved_data)
                    elif response.status >= 500:
                        raise TixteServerError(response, resolved_data)
                    else:
                        raise HTTPException(response, resolved_data)

        # We've run into a problem, let's close all of the files
        if files is not None:
            for file in files:
                file.close()

        if response is not None:
            if response.status >= 500:
                raise TixteServerError(response, resolved_data)

            raise HTTPException(response, resolved_data)

        raise RuntimeError('Unreachable code in HTTP handling')

    async def get_from_url(self, url: str) -> bytes:
        if self.session is None:
            self.session = aiohttp.ClientSession()

        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.read()
            elif response.status == 404:
                raise NotFound(response, 'asset not found')
            elif response.status == 403:
                raise Forbidden(response, 'cannot retrieve asset')
            else:
                raise HTTPException(response, 'failed to get asset')

    def upload(
        self, file: File, *, domain: Optional[Union[Domain, str]] = None, upload_type: int
    ) -> Response[upload.Upload]:
        r = Route('POST', '/upload')

        data: Dict[str, Any] = {
            'domain': (domain and str(domain)) or self.domain,
            'type': upload_type,
            "name": file.filename,
            "upload_source": "dashboard",
        }

        return self.request(r, files=[file], json=data)

    def delete_upload(self, upload_id: str) -> Response[base.Message]:
        r = Route('DELETE', '/users/@me/uploads/{upload_id}', upload_id=upload_id)
        return self.request(r)

    # NOTE: Tixte removed this endpoint.
    # def get_upload(self, upload_id: str) -> Response[upload.Upload]:
    #     r = Route('GET', '/users/@me/uploads/{upload_id}', upload_id=upload_id)
    #     return self.request(r)

    def get_upload_permissions(self, upload_id: str) -> Response[List[upload.UploadPermission]]:
        r = Route('GET', '/users/@me/uploads/{upload_id}/permissions', upload_id=upload_id)
        return self.request(r)

    def get_uploads(self) -> Response[upload.BulkGetUploads]:
        r = Route('GET', '/users/@me/uploads')
        return self.request(r)

    def add_upload_permissions(
        self,
        *,
        upload_id: str,
        user_id: str,
        permission_level: Literal[1, 2, 3],
        message: Optional[str] = None,
    ) -> Response[upload.UploadPermission]:
        r = Route('POST', '/users/@me/uploads/{upload_id}/permissions', upload_id=upload_id)

        data = {'permission_level': permission_level, 'user': user_id}
        if message is not None:
            data['message'] = message

        return self.request(r, data=data)

    def remove_upload_permissions(self, *, upload_id: str, user_id: str) -> Response[Dict[str, Any]]:
        #  {"success":true,"data":{}}
        r = Route(
            'DELETE',
            '/users/@me/uploads/{upload_id}/permissions/{user_id}',
            upload_id=upload_id,
            user_id=user_id,
        )
        return self.request(r)

    def edit_upload_permissions(self, *, upload_id: str, user_id: str, permission_level: Literal[1, 2, 3]) -> Response[Any]:
        r = Route(
            'PATCH',
            '/users/@me/uploads/{upload_id}/permissions/{user_id}',
            upload_id=upload_id,
            user_id=user_id,
        )
        return self.request(r, json={'permission_level': permission_level})

    def search_uploads(
        self,
        *,
        query: str,
        domains: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
        limit: Optional[int] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        sort_by: Optional[str] = None,
        permission_levels: Optional[List[int]] = None,
    ) -> Response[List[Any]]:
        data: Dict[str, Any] = {'query': query}

        if domains is not None:
            data['domains'] = domains

        if extensions is not None:
            data['extensions'] = extensions

        if limit is not None:
            data['limit'] = limit

        if min_size is not None:
            data.setdefault('size', {})['min'] = min_size

        if max_size is not None:
            data.setdefault('size', {})['max'] = max_size

        if sort_by is not None:
            data['sort_by'] = sort_by

        if permission_levels is not None:
            data['permission_levels'] = permission_levels

        r = Route('POST', '/users/@me/uploads/search')
        return self.request(r, json=data)

    def get_client_user(self) -> Response[user.ClientUser]:
        r = Route('GET', '/users/@me')
        return self.request(r)

    def get_user(self, user_id: str) -> Response[user.User]:
        r = Route('GET', '/users/{user_id}', user_id=user_id)
        return self.request(r)

    # NOTE: Private endpoint:
    def search_user(self, query: str, limit: int = 6) -> Response[List[user.User]]:
        r = Route('POST', 'users/search')
        data = {'query': query, 'limit': limit}
        return self.request(r, json=data)

    def get_domains(self) -> Response[Any]:
        r = Route('GET', '/users/@me/domains')
        return self.request(r)

    # NOTE: Not implemented
    def get_domain(self) -> Response[Any]:
        ...

    def create_domain(self, domain: str, *, custom: bool = False) -> Response[Any]:
        r = Route('PATCH', '/users/@me/domains')
        data = {'domain': domain, 'custom': custom}
        return self.request(r, json=data)

    def delete_domain(self, domain: str) -> Response[Any]:
        # {"success":true,"data":{"message":"Domain successfully deleted","domain":"foo_bar.tixte.co"}}
        r = Route('DELETE', '/users/@me/domains/{domain}', domain=domain)
        return self.request(r)

    def get_config(self) -> Response[Any]:
        r = Route('GET', '/users/@me/config')
        return self.request(r)

    def get_upload_key(self) -> Response[Dict[str, Any]]:
        # {"success":true,"data":{"api_key":"..."}}
        r = Route('GET', '/users/@me/keys')
        return self.request(r)

    def get_subscriptions(self) -> Response[Dict[str, Any]]:
        r = Route('GET', '/users/@me/billing/subscriptions')
        return self.request(r)

    def get_payment_methods(self) -> Response[Dict[str, Any]]:
        r = Route('GET', '/users/@me/billing/payment-methods')
        return self.request(r)

    def get_transactions(self) -> Response[Dict[str, Any]]:
        r = Route('GET', '/users/@me/billing/transactions')
        return self.request(r)

    def get_developer_applications(self) -> Response[Dict[str, Any]]:
        r = Route('GET', '/users/@me/developer/applications')
        return self.request(r)

    def get_settings(self) -> Response[Dict[str, Any]]:
        r = Route('GET', '/users/@me/settings')
        return self.request(r)

    def update_settings(
        self,
        *,
        new_login: Optional[bool] = None,
        promotional: Optional[bool] = None,
        shared_file: Optional[bool] = None,
        addable: Optional[bool] = None,
        shareable: Optional[int] = None,
    ) -> Response[Dict[str, Any]]:
        emails: Dict[str, Any] = {}

        if new_login is not None:
            emails['new_login'] = new_login

        if promotional is not None:
            emails['promotional'] = promotional

        if shared_file is not None:
            emails['shared_file'] = shared_file

        privacy: Dict[str, Any] = {}

        if addable is not None:
            privacy['addable'] = addable

        if shareable is not None:
            privacy['shareable'] = shareable

        data: Dict[str, Any] = {}

        if emails:
            data['emails'] = emails

        if privacy:
            data['privacy'] = privacy

        r = Route('PATCH', '/users/@me/settings')
        return self.request(r, json=data)

    def request_data(self) -> Response[Dict[str, Any]]:
        r = Route('POST', '/users/@me/data-requests')
        return self.request(r)

    def update_config(
        self,
        *,
        author_name: Optional[str] = None,
        author_url: Optional[str] = None,
        description: Optional[str] = None,
        provider_name: Optional[str] = None,
        provider_url: Optional[str] = None,
        theme_color: Optional[str] = None,
        title: Optional[str] = None,
        custom_css: Optional[str] = None,
    ) -> Response[Any]:
        embed: Dict[str, str] = {}

        if author_name is not None:
            embed['author_name'] = author_name

        if author_url is not None:
            embed['author_url'] = author_url

        if description is not None:
            embed['description'] = description

        if provider_name is not None:
            embed['provider_name'] = provider_name

        if provider_url is not None:
            embed['provider_url'] = provider_url

        if theme_color is not None:
            embed['theme_color'] = theme_color

        if title is not None:
            embed['title'] = title

        data: Dict[str, Any] = {}

        if embed:
            data['embed'] = embed

        if custom_css is not None:
            data['custom_css'] = custom_css

        r = Route('PATCH', '/users/@me/config')
        return self.request(r, json=data)

    def get_total_upload_size(self) -> Response[Any]:
        r = Route('GET', '/users/@me/uploads/size')
        return self.request(r)

    async def url_to_file(self, *, url: str, filename: Optional[str]) -> File:
        data = await self.get_from_url(url)
        bytes_io = io.BytesIO(data)
        return File(bytes_io, filename=filename)
