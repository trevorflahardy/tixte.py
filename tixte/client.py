import aiohttp
import io
from typing import Optional

from .http import HTTP
from .file import File, FileResponse

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
    """
    __slots__ = ('session', 'domain', '_http',)
    
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
    
    async def url_to_file(
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
    