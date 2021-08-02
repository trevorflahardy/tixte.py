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

import re
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
)

from .errors import (
    NoDomain,
    Forbidden,
    NotFound,
    TixteServerError,
    HTTPException
)
from .file import File
from . import utils


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
    __slots__ = ('session', 'master_key', 'domain')
    
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
        
    async def _json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
        text = await response.text(encoding='utf-8')
        try:
            if response.headers.get('content-type' )== 'application/json':
                return utils.to_json(text)
        except KeyError:
            pass

        return text

    async def request(self, route: Route, **kwargs: Any) -> Dict:
        method = route.method
        url = route.url

        kwargs['headers'] = {
            'Authorization': self.master_key
        }
        
        response: Union[aiohttp.ClientResponse, None] = None
        for tries in range(5):
            async with self.session.request(method, url, **kwargs) as response:
                data = await self._json_or_text(response)
                
                if 300 > response.status >= 200:  # Everything is ok
                    return data
                
                if response.status == 429:   # We're rate limited
                    retry_after: float = response.headers.get('x-ratelimit-reset')  # time (in seconds) before rate limit gets reset
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