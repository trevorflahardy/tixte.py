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
from typing import (
    TYPE_CHECKING,
    Union,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Coroutine,
)
from typing_extensions import ParamSpec, Self

from .http import HTTP
from .state import State
from .abc import Object
from .config import Config
from .upload import Upload, PartialUpload
from .errors import NotFound

if TYPE_CHECKING:
    import aiohttp

    from .user import User, ClientUser
    from .file import File
    from .domain import Domain

__all__: Tuple[str, ...] = ('Client',)

T = TypeVar('T')
P = ParamSpec('P')
AnyCoro = Coroutine[Any, Any, T]
EventCoro = Callable[P, AnyCoro[T]]


class Client(Object):
    """
    The base Client for the wrapper. Every method on the Client class is used to get
    other objects from the API. The client should be used as a context manager to ensure
    the cleanup of the aiohttp session, but it doesn't have to be.

    .. code-block:: python3

        async with tixte.Client('master_key', 'domain') as client:
            user = await client.fetch_user(user_id)
            print(user)

    Parameters
    ----------
    master_key: :class:`str`
        Your Tixte master key. Notes on how this can be obtained can be found
        on the github readme.
    domain: :class:`str`
        The domain you want to upload to.
        If you haven't already, you need to create a domain at `https://tixte.com/dashboard/domains`
    session: Optional[:class:`aiohttp.ClientSession`]
        An optional session to pass for HTTP requests. If not provided, a new session will be created
        for you.
    """

    def __init__(
        self,
        master_key: str,
        domain: str,
        /,
        *,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self._http = HTTP(
            master_key=master_key,
            domain=domain,
            session=session,
            dispatch=self.dispatch,
        )

        self._state: State = State(dispatch=self.dispatch, http=self._http)
        self._state._get_client = lambda: self  # type: ignore

        self._listeners: Dict[str, List[Callable[..., Any]]] = {}

    async def __aenter__(self) -> Self:
        if self._http.session is None:
            await self._http.create_client_session()

        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.cleanup()

    # Internal helpers for dispatching

    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> List[asyncio.Task[Any]]:
        event_fmt = 'on_' + event
        tasks: List[asyncio.Task[Any]] = []

        method = getattr(self, event_fmt, None)
        if method:
            tasks.append(
                asyncio.create_task(
                    method(*args, **kwargs),
                    name=f'tixte-dispatcher-{event_fmt}',
                )
            )

        callables = self._listeners.get(event_fmt, [])
        for item in callables:
            tasks.append(
                asyncio.create_task(item(*args, **kwargs), name=f'tixte-dispatcher-{event_fmt}')
            )

        return tasks

    def event(self, event: Optional[str] = None) -> Callable[[EventCoro[P, T]], EventCoro[P, T]]:
        """A decorator used to register a coroutine as a listener for an event.

        .. code-block:: python3

            @client.event('on_request')
            async def on_request(response: aiohttp.ClientRequest):
                print('We requested something!', response.status)

        Parameters
        ----------
        event: Optional[:class:`str`]
            The event to listen for. If not provided, the name of the coroutine will be used.
        """

        def wrapped(func: EventCoro[P, T]) -> EventCoro[P, T]:
            if not asyncio.iscoroutinefunction(func):
                raise TypeError('event callback must be a coroutine')

            event_name = event or func.__name__

            if not event_name.startswith('on_'):
                raise ValueError('event name must start with \'on_\'')

            self._listeners.setdefault(event_name, []).append(func)

            return func

        return wrapped

    def remove_listener(self, event: str, *, callback: Optional[EventCoro[P, T]] = None) -> None:
        """A method to remove a listener from an event.

        Parameters
        ----------
        event: :class:`str`
            The event to remove the listener from.
        callback: Optional[Callable]
            The callback to remove. If not provided, all listeners for the event will be removed.
        """
        if not callback:
            self._listeners.pop(event, None)
            return
        else:
            listeners = self._listeners.get(event, [])
            if not listeners:
                return

            try:
                listeners.remove(callback)
            except ValueError:
                pass

    # Begin public methods

    @property
    def user(self) -> Optional[ClientUser]:
        """Optional[:class:`ClientUser`]: The client's user, if in the internal cache."""
        return self._state.client_user

    @property
    def users(self) -> List[User]:
        """List[:class:`User`]: A list of all users within the internal cache."""
        return list(self._state.users.values())

    @property
    def domains(self) -> List[Domain]:
        """List[:class:`Domain`]: A list of all domains within the internal cache."""
        return list(self._state.domains.values())

    async def cleanup(self) -> None:
        """|coro|

        A helper coroutine used to cleanup the client's HTTP session.
        """
        if not self._http.session:
            raise ValueError('No session to cleanup')

        await self._http.session.close()

    def get_user(self, id: str, /) -> Optional[User]:
        """Used to get a user from the internal cache of users.

        Parameters
        ----------
        id: :class:`str`
            The ID of the user to get.

        Returns
        -------
        Optional[:class:`User`]
            The user with the given ID, if it exists within the internal cache.
        """
        return self._state.get_user(id)

    def get_domain(self, url: str) -> Optional[Domain]:
        """Gets a domain from the internal cache of domains.

        Parameters
        ----------
        url: :class:`str`
            The url of the domain to get.

        Returns
        -------
        Optional[:class:`Domain`]
            The domain with the given url, if it exists within the internal cache.
        """
        return self._state.get_domain(url)

    def get_partial_upload(self, id: str, /) -> PartialUpload:
        """A method used to get a partial upload from its ID.

        Parameters
        ----------
        id: :class:`str`
            The ID of the partial upload to get.

        Returns
        -------
        :class:`PartialUpload`
            The partial upload with the given ID.
        """
        return PartialUpload(state=self._state, id=id)

    async def fetch_user(self, id: str, /) -> User:
        """|coro|

        A coroutine used to fetch a user from its ID.

        Parameters
        ----------
        id: :class:`str`
            The ID of the user to fetch.

        Returns
        -------
        Optional[:class:`User`]
            The user with the given ID, if it exists within the internal cache.

        Raises
        ------
        Forbidden
            You do not have permission to fetch the user.
        NotFound
            The user with the given ID does not exist.
        HTTPException
            An HTTP error occurred.
        """
        data = await self._http.get_user(id)
        return self._state.store_user(data)

    async def upload(self, file: File, /, *, domain: Optional[Union[Domain, str]] = None) -> Upload:
        """|coro|

        A coroutine used to upload a file to Tixte.

        Parameters
        ----------
        file: :class:`File`
            The file to upload. Please note `discord.py's file objects <https://discordpy.readthedocs.io/en/latest/api.html?highlight=file#discord.File>`_ as well.
        domain: Optional[Union[:class:`Domain`, :class:`str`]]
            Optionally, upload to a different domain than the client's default.

        Returns
        -------
        :class:`Upload`
            The response from the upload.

        Raises
        ------
        Forbidden
            You do not have permission to upload this file.
        HTTPException
            An HTTP exception has occurred.
        """
        data = await self._http.upload(file, filename=file.filename, domain=domain)
        return Upload(state=self._state, data=data)

    async def url_to_file(self, url: str, /, *, filename: Optional[str] = None) -> File:
        """|coro|

        A helper coroutine to convert a URL to a :class:`File`.

        Parameters
        ----------
        url: :class:`str`
            The URL to convert.
        filename: Optional[:class:`str`]
            The filename to use for the file. If not provided, ``attachment1`` will be used
            instead.

        Returns
        -------
        :class:`File`
            The file with the given URL.
        """
        return await self._http.url_to_file(url=url, filename=filename or 'attachment1')

    async def fetch_client_user(self) -> ClientUser:
        """|coro|

        A coroutine used to fetch the client's user. Once fetched for the first time,
        this can be accessed via the :attr:`user` attribute.

        Returns
        -------
        :class:`ClientUser`
            The client's user.
        """
        data = await self._http.get_client_user()
        return self._state.store_client_user(data)

    async def fetch_domains(self) -> List[Domain]:
        """|coro|

        A coroutine to fetch all domains registered with Tixte. Once fetched
        once, you can get all of the domains via :attr:`domains`.

        Returns
        -------
        List[:class:`Domain`]
            A list of all domains registered with Tixte.
        """
        data = await self._http.get_domains()

        for entry in data['domains']:
            self._state.store_domain(entry)

        return list(self._state.domains.values())

    async def fetch_config(self) -> Config:
        """|coro|

        A coroutine used to fetch the configuration settings
        you have within Tixte.

        Returns
        -------
        :class:`Config`
            The configuration settings.
        """
        data = await self._http.get_config()
        return Config(state=self._state, data=data)

    async def fetch_upload(self, upload_id: str, /) -> Upload:
        """|coro|

        Fetch an upload from its ID. Please note this is a wrapper around
        :meth:`search_upload` as the API doesn't have a direct endpoint
        for fetching an upload.

        Parameters
        ----------
        upload_id: :class:`str`
            The ID of the upload to fetch.

        Returns
        -------
        :class:`Upload`
            The upload that was requested.

        Raises
        ------
        Forbidden
            You do not have permission to fetch this upload.
        HTTPException
            An HTTP exception has occurred.
        """
        data = await self._http.search_upload(query=upload_id, limit=1)
        if not data:
            raise NotFound(None, data, 'Upload not found!')

        return Upload(state=self._state, data=data[0])

    async def fetch_uploads(self) -> List[Upload]:
        """|coro|

        Fetches all of the existing uploads from Tixte.

        Returns
        -------
        List[:class:`Upload`]
            A list of all uploads that you have uploaded to Tixte.
        """
        data = await self._http.get_uploads()
        return [Upload(state=self._state, data=entry) for entry in data['uploads']]

    async def search_upload(
        self,
        query: str,
        /,
        *,
        domains: List[Domain] = [],
        limit: int = 48,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        sort_by: str = 'relevant',
    ) -> List[Upload]:
        """|coro|

        Search for an upload by its name.

        Parameters
        ----------
        query: :class:`str`
            The query to search for.
        domains: List[:class:`Domain`]
            Limit your query to a specific domain(s).
        limit: :class:`int`
            The maximum number of results to return. This defaults to ``48`` as that's
            what Tixte defaults to.
        min_size: Optional[:class:`int`]
            The minimum size of the upload. Defaults to ``None``.
        max_size: Optional[:class:`int`]
            The maximum size of the upload. Defaults to ``None``.
        sort_by: :class:`str`
            The sort order of the results. This defaults to ``relevant``. Other sort_by options
            are currently unknown.

        Returns
        -------
        List[:class:`Upload`]
            A list of all uploads that match the query.
        """
        data = await self._http.search_upload(
            query=query,
            domains=[d.url for d in domains],
            limit=limit,
            min_size=min_size,
            max_size=max_size,
            sort_by=sort_by,
        )
        return [Upload(state=self._state, data=entry) for entry in data]

    # NOTE: Not a public endpoint :)
    # async def search_user(self, name: str, /, *, limit: int = 6) -> List[User]:
    #     """|coro|
    #
    #     Search for a user by name.
    #
    #     Parameters
    #     ----------
    #     name: :class:`str`
    #         The name of the user to search for.
    #     limit: Optional[:class:`int`]
    #         The maximum number of users to return. Defaults to ``6`` as that's what Tixte uses.
    #
    #     Returns
    #     -------
    #     List[:class:`User`]
    #         A list of users that match the search.
    #     """
    #     data = await self._http.search_user(name, limit=limit)
    #     return [self._state.store_user(entry) for entry in data]

    async def create_domain(self, domain: str, /, *, is_custom: bool = False) -> Domain:
        """|coro|

        Create a domain on Tixte.

        Parameters
        ----------
        domain: :class:`str`
            The url of the domain to create.
        is_custom: Optional[:class:`bool`]
            Denotes if the domain is a custom domain that you personally own, instead of a subdomain
            that tixte creates for you. If ``False``, than the domain must end in ``tixte.co``, ``likes.cash``,
            ``discowd.com``, ``has.rocks``, ``is-from.space``, ``bot.style``, ``needs.rest``, or ``wants.solutions``.

        Returns
        -------
        :class:`Domain`
            The domain that was created.
        """
        await self._http.create_domain(domain, custom=is_custom)
        owner = self.user or await self.fetch_client_user()
        return self._state.store_domain({'name': domain, 'uploads': 0, 'owner': owner.id})

    async def fetch_upload_key(self) -> str:
        """|coro|

        Fetches your Tixte upload key. This upload key can be used on ``Tixte Snap``, ``ShareX``, or ``MagicCap``.
        You can learn more on your Tixte Dashboard under the "Integrations" section.

        Returns
        --------
        :class:`str`
            Your upload key.
        """
        data = await self._http.get_upload_key()
        return data['api_key']
