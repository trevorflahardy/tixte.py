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

import aiohttp
import io
from typing import Optional, List

from .http import HTTP
from .file import File, FileResponse
from .user import ClientUser, User
from .errors import NotFound
from .domain import Domain
from .config import Config

__all__ = (
    'Client',
)

class Client:
    r"""
    The base Client for the wrapper. 
    We'll use this to contain everything and keep it simple.
    
    Parameters
    ----------
    master_key: :class:`str`
        Your Tixte master key. 
        
        How to obtain:
            > Go to: https://tixte.com/dashboard/configurations
            
            > Go to the Console via pressing Ctrl + Shift + I 
            
            > Paste in `document.cookie.split("tixte_auth=")[1].split(";")[0]` at the bottom and press enter
            
            > Your key should be outputted.
            
    domain: Optional[:class:`str`]
        The domain you want to upload to. 
        If you haven't already, you need to create a domain at `https://tixte.com/dashboard/domains`
        
        ..note:
            If no domain is specified, the domain with the most amount of uploads will be defaulted.
        
    session: Optional[:class:`aiohttp.ClientSession`]
        An optional session to pass into the client for requests.
        
    Methods
    -------
    upload_file:
        Upload a file to Tixte.
    delete_file:
        Delete a file from Tixte.
    fetch_user:
        Fetch a user.
    file_from_url:
        Turn an image URL to a File object.
    """
    def __init__(
        self,
        master_key: str,
        *,
        domain: Optional[str] = None,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._session = session or aiohttp.ClientSession()
        self._http = HTTP(master_key, domain=domain, session=self._session)
        
    async def upload_file(self, file: File) -> FileResponse:
        """
        Upload a file.
        
        Parameters
        ----------
        file: :class:`File`
            The file obj to upload.
        
        Returns
        -------
        :class:`FileResponse`
        """
        data = await self._http.upload_file(file=file)
        return FileResponse(self._http, data)
    
    async def delete_file(self, upload_id: str) -> None:
        """
        Delete a file from it's upload id.
        
        Parameters
        ----------
        upload_id: :class:`str`
            The upload_id to delete from. 
            
            .. note::
                This can not be a File obj. If you wish to delete a file directly
                you can do:
                
                ```python
                await file.delete()
                ```
                
        Returns
        -------
        None
        """
        return await self._http.delete_file(upload_id)
    
    async def fetch_config(self) -> Config:
        """
        Fetch your user config. This is mostly the configuration tab on Tixte.
        
        Returns
        -------
        :class:`Config`
        """
        data = await self._http.fetch_config()
        return Config(self._http, data)
    
    async def fetch_client_user(
        self,
        *, 
        set_attrs_to_client: bool = False
    ) -> ClientUser:
        """
        Fetch your user. and get some useful information back.
        
        Parameters
        ----------
        set_attrs_to_client: Optional[:class:`bool`] = False
            If you're fetching a ClientUser, you can choose to set all attrs from the ClientUser
            onto the Client. This means you wouldn't have to do the fetch_user more then once for
            client information.
            
            ```python
            await client.fetch_user(set_attrs_to_client=True)
            print(client.id)
            print(client.email)
            ```
        
        Returns
        -------
        :class:`ClientUser`
        """
        data = await self._http.fetch_client_user()
        user = ClientUser(self._http, data)
        if set_attrs_to_client:
            user._dump_attrs_to_client(self)
        return user
                
    async def fetch_user(
        self, 
        user_id: str
    ) -> User:
        """
        Fetch a user and get some useful information back.
        
        ..note:
            If no user_id is specified, a :class:`ClientUser` will be returned.
            A ClientUser is yourself.
            
        Parameters
        ----------
        user_id: str
            The user_id you want to fetch. This can also work with user name.
            
        Returns
        -------
        :class:`User`
        """
        data = await self._http.fetch_user(user_id)
        return User(self._http, data)
    
    async def fetch_domains(self) -> Optional[List[Domain]]:
        """
        Get all your domain data.
        
        Returns
        -------
        :class:`Domain`
        """
        data = await self._http.fetch_domains()
        domains = []
        for entry in data['domains']:
            local_domain = Domain(entry)
            if hasattr(self, '_raw_user'):
                if self.id == entry['owner']:  # We own this
                    user = User(self._http, self._raw_user)
                    local_domain.owner = user
                    domains.append(local_domain)
                    continue
            try:
                user = await self.fetch_user(entry['owner'])
                local_domain.owner = user
            except NotFound:
                continue
            domains.append(local_domain)
            
        return domains

    async def url_to_file(
        self, 
        url: str, 
        *,
        filename: str
    ) -> Optional[File]:
        """
        Use a file URL and turn it into a File obj.
        
        Parameters
        ----------
        url: :class:`str`
            The url to turn into a file obj.
        filename: :class:`str`
            The filename you want the File obj to be.
            
        Returns
        -------
        :class:`File`
        """
        return await self._http.url_to_file(url=url, filename=filename)
    