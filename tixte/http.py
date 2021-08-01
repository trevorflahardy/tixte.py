import aiohttp

from typing import (
    ClassVar,
    Any,
    Optional,
    Dict
)

from .errors import HTTPException
from .file import File


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
    __slots__ = ('BASE', 'method', 'path', 'url')
    
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
    __slots__ = ('session', 'upload_key', 'domain')
    
    def __init__(
        self, 
        upload_key: str,
        domain: str,
        *,
        session: aiohttp.ClientSession
    ) -> None:
        self.session = session
        self.upload_key = upload_key
        self.domain = domain
    
    async def request(self, route: Route, **kwargs: Any) -> Dict:
        method = route.method
        url = route.url

        kwargs['headers'] = {
            'Authorization': self.upload_key
        }
        
        async with self.session.request(method, url, **kwargs) as resp:
            data = await resp.json()
            data = data['data']
            if resp.status != 200:
                raise HTTPException(data['message'])
            return data
    
    def upload_file(self, file: File) -> Optional[Dict]:
        data = aiohttp.FormData()
        data.add_field('file', file.fp, filename=file.filename, content_type='application/octet-stream')
        
        r = Route('POST', '/upload?domain={domain}', domain=self.domain)
        return self.request(r, data=data)
    
    def delete_file(self, upload_id: str) -> None:
        r = Route('DELETE', '/users/@me/uploads/{upload_id}', upload_id=upload_id)
        return self.request(r)