import aiohttp
import io
from typing import Optional, Union

from .http import HTTP
from .file import File, FileResponse
from .user import ClientUser, User

__all__ = (
    'Client',
)

class Client:
    r"""
    The base Client for the wrapper. 
    We'll use this to contain everything and keep it simple.
    
    Parameters
    ----------
    upload_key: :class:`str`
        Your personal Tixte upload key. Can be found at `https://tixte.com/dashboard/configurations`
    domain: :class:`str`
        The domain you want to upload to. 
        If you haven't already, you need to create a domain at `https://tixte.com/dashboard/domains`
    session: Optional[:class:`aiohttp.ClientSession`]
        An optional session to pass into the client for requests.
        
    Attributes
    ----------
    domain:
        The domain you set the client to use.
        
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
        upload_key: str,
        domain: str,
        *,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.domain = domain
        self.session = session or aiohttp.ClientSession()
        self._http = HTTP(upload_key, self.domain, session=self.session)
        
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
    
    async def fetch_user(
        self, 
        user_id: Optional[str] = None, 
        *, 
        set_attrs_to_client: bool = False
    ) -> Union[ClientUser, User]:
        """
        Fetch a user and get some useful information back.
        
        ..note:
            If no user_id is specified, a :class:`ClientUser` will be returned.
            A ClientUser is yourself.
            
        Parameters
        ----------
        user_id: Optional[:class:`str`]
            The user_id you want to fetch. If none is specified, a ClientUser will be returned.
        set_attrs_to_client: Optional[:class:`bool`] = False
            If you're fetching a ClientUser, you can choose to set all attrs from the ClientUser
            onto the Client. This means you wouldn't have to do the fetch_user more then once for
            client information.
            
            ```python
            await client.fetch_user(set_attrs_to_client=True)
            print(client.id)
            print(client.email)
            ```
        """
        if not user_id:
            data = await self._http.fetch_client_user()
            user = ClientUser(self._http, data)
            if set_attrs_to_client:
                user._dump_attrs_to_client(self)
        else:
            data = await self._http.fetch_user(user_id)
            user = User(self._http, data)
        return user
    
    async def file_from_url(
        self, 
        url: str, 
        filename: str = 'file.png'
    ) -> Optional[File]:
        """
        Use a file URL and turn it into a File obj.
        
        Parameters
        ----------
        url: :class:`str`
            The url to turn into a file obj.
        filename: Optional[:class:`str`]
            The filename you want the File obj to be.
            
        Returns
        -------
        :class:`File`
        """
        async with self.session.get(url) as resp:
            if resp.status != 200:
                return None
            bytes = io.BytesIO(await resp.read())
            bytes.seek(0)
        
        return File(bytes, filename=filename)
    