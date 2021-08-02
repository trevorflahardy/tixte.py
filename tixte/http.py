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

import io
import sys
import aiohttp
import asyncio
import logging

from typing import (
    ClassVar,
    Any,
    Optional,
    Dict,
    Union,
    Dict,
    Final
)

from .errors import (
    NoDomain,
    Forbidden,
    NotFound,
    TixteServerError,
    HTTPException
)
from .file import File
from . import utils, __version__


__all__ = (
    'Route',
    'HTTP'
)

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
    __slots__ = ('method', 'path', 'url')
    
    BASE: ClassVar[str] = 'https://api.tixte.com/v1'
    
    def __init__(
        self, 
        method: str, 
        path: str, 
        **parameters: Any
    ) -> None:
        if parameters:
            try:
                path = path.format(**parameters)
            except IndexError:
                pass
            
        self.path: str = path
        self.url: str = self.BASE + self.path
        self.method: str = method
        
        
class HTTP:
    __slots__ = ('session', 'master_key', 'domain', 'user_agent')
    
    # Dis var taken from d.py :blobsweats:
    # https://github.com/Rapptz/discord.py/blob/master/discord/http.py#L163
    REQUEST_LOG: ClassVar[str] = '{method} {url} with {json} has returned {status}'  
    
    def __init__(
        self, 
        master_key: str,
        *,
        domain: Optional[str] = None,
        session: aiohttp.ClientSession
    ) -> None:
        self.master_key = master_key
        self.domain = domain
        self.session = session
        
        user_agent = 'TixteClient (https://github.com/NextChai/Tixte {0}) Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        
    async def _json_or_text(self, response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
        text = await response.text(encoding='utf-8')
        if response.headers.get('Content-Type') == 'application/json; charset=utf-8':
            return utils.to_json(text)
        return text

    async def request(self, route: Route, **kwargs: Any) -> Dict:
        method = route.method
        url = route.url

        kwargs['headers'] = {
            'Authorization': self.master_key,
            'User-Agent': self.user_agent
        }
        
        response: Union[aiohttp.ClientResponse, None] = None
        for tries in range(5):
            async with self.session.request(method, url, **kwargs) as response:
                data = await self._json_or_text(response)
                
                logging.debug(f'Recieved HTTP Status of {response.status}')
                logging.debug(f'Time (in seconds) before rate limit gets reset: {response.headers.get("x-ratelimit-reset")}')
                logging.debug(f'Amount of reqs left before hitting the limit: {response.headers.get("x-ratelimit-remaining")}')
                
                if 300 > response.status >= 200:  # Everything is ok
                    logging.debug(self.REQUEST_LOG.format(method=method, url=url, json=data, status=response.status))
                    
                    if data.get('data'):
                        return data['data']
                    return data
                
                if response.status == 429:   # We're rate limited
                    headers = response.headers
                    retry_after: float = float(headers.get('x-ratelimit-reset'))  # Retry the status after this amount of time
                    if retry_after == 0 and not headers.get('x-ratelimit-remaining'):
                        retry_after: float = float(headers.get('Retry-After'))
                    
                    fmt = f'We are being rate limited! Trying again in {retry_after} seconds.'
                    logging.warning(fmt)
                    
                    await asyncio.sleep(retry_after)  # Sleep until no ratelimit :ok_hand:
                    continue
                
                if response.status in {500, 502, 504}:  # Taken from d.py yayy
                    await asyncio.sleep(1 + tries * 2)
                    continue
                
                if response.status == 403:
                    raise Forbidden(response, data)
                elif response.status == 404:
                    raise NotFound(response, data)
                elif response.status >= 500:
                    raise TixteServerError(response, data)
                else:
                    raise HTTPException(response, data)
                
        if response is not None:
            if response.status >= 500:
                raise TixteServerError(response, data)
            raise HTTPException(response, data)
        raise RuntimeError('Unreachable code in HTTP handling')
                    
    async def _get_domain_if_none(self):
        data = await self.fetch_domains()
        print(data)
        if data['total'] < 1:
            raise NoDomain("You have not made any domains yet. This process was cancelled.")
        
        return data['domains'][0]['name']
    
    async def upload_file(self, file: File) -> Optional[Dict]:
        data = aiohttp.FormData()
        data.add_field('file', file.fp, filename=file.filename, content_type='application/octet-stream')
        
        if not self.domain:
            self.domain = await self._get_domain_if_none()
            logging.info(f"New domain used because none specified: {self.domain}")
    
        r = Route('POST', '/upload?domain={domain}', domain=self.domain)
        return await self.request(r, data=data)
    
    def delete_file(self, upload_id: str) -> None:
        r = Route('DELETE', '/users/@me/uploads/{upload_id}', upload_id=upload_id)
        return self.request(r)

    def fetch_client_user(self) -> Optional[Dict]:
        r = Route('GET', '/users/@me')
        return self.request(r)
    
    def fetch_user(self, user_id: str) -> Optional[Dict]:
        r = Route('GET', '/users/{user_id}', user_id=user_id)
        return self.request(r)
    
    def fetch_domains(self) -> Optional[Dict]:
        r = Route('GET', '/users/@me/domains')
        return self.request(r)
    
    def fetch_config(self) -> Optional[Dict]:
        r = Route('GET', '/users/@me/config')
        return self.request(r)
    
    async def url_to_file(
        self, 
        *,
        url: str, 
        filename: str
    ) -> File:
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return None
            bytes = io.BytesIO(await resp.read())
            bytes.seek(0)
        
        return File(bytes, filename=filename)