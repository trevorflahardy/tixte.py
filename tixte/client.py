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
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import ParamSpec, Self

from tixte.enums import UploadType

from .abc import Object
from .config import Config
from .errors import NotFound
from .http import HTTP
from .state import State
from .upload import PartialUpload, Upload

if TYPE_CHECKING:
    import aiohttp

    from .domain import Domain
    from .file import File
    from .user import ClientUser, User

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

    .. container:: operations

        .. describe:: async with x

            Enters the client as a context manager. This will automatically
            cleanup the :class:`aiohttp.ClientSession` when the context is exited. Optionally,
            you can manage the :class:`aiohttp.ClientSession` yourself and pass it to the client. Regardless
            of which you do, the client will always close the session when the context is exited.

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
        If you haven't already, you need to create a domain at `the tixte domain dashboard <https://tixte.com/dashboard/domains>`_.
    session: Optional[:class:`aiohttp.ClientSession`]
        An optional session to pass for HTTP requests. If not provided, a new session will be created
        for you.
    fetch_client_user_on_start: Optional[:class:`bool`]
        Whether to fetch the client's user on startup. This means the :attr:`user` method will be :class:`ClientUser`
        100% of the time. Defaults to ``False``. Please note this is only valid if you are using the client
        within a context manager setting. Otherwise, no user will be fetched.

    Attributes
    ----------
    fetch_client_user_on_start: :class:`bool`
        Whether to fetch the client's user on startup. This means the :meth:`fetch_client_user`
        method will be called upon entering the client as a context manager. Defaults to ``False``.
    """

    def __init__(
        self,
        master_key: str,
        domain: str,
        /,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        fetch_client_user_on_start: bool = False,
    ) -> None:
        self._http = HTTP(
            master_key=master_key,
            domain=domain,
            session=session,
            dispatch=self.dispatch,
        )

        self._state: State = State(http=self._http)
        self._state._get_client = lambda: self

        self._listeners: Dict[str, List[Callable[..., Any]]] = {}
        self._waiters: Dict[str, List[Tuple[asyncio.Future[Any], Optional[Callable[[Any], Optional[bool]]]]]] = {}

        self.fetch_client_user_on_start: bool = fetch_client_user_on_start

    async def __aenter__(self) -> Self:
        if self._http.session is None:
            await self._http.create_client_session()

        if self.fetch_client_user_on_start:
            await self.fetch_client_user()

        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.cleanup()

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

    # Internal helper for dispatching
    def dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        event_fmt = 'on_' + event
        method = getattr(self, event_fmt, None)
        if method:
            asyncio.create_task(
                method(*args, **kwargs),
                name=f'tixte-dispatcher-{event_fmt}',
            )

        callables = self._listeners.get(event_fmt, [])
        if callables:
            for item in callables:
                asyncio.create_task(item(*args, **kwargs), name=f'tixte-dispatcher-{event_fmt}')

        waiters = self._waiters.get(event_fmt, [])
        if waiters:
            for future, condition in waiters:
                result = None
                if condition is not None:
                    result = condition(*args, **kwargs)

                if not result:
                    continue

                if future.done():
                    continue

                # Any waiters can not accept kwargs, so we will ignore them. There are
                # also no waiters that *should* accept kwargs at this moment.
                future.set_result(*args)

                waiters.remove((future, condition))

    def listen(self, event: Optional[str] = None) -> Callable[[EventCoro[P, T]], EventCoro[P, T]]:
        """A decorator that registers an event to listen for. This is used to register
        an event to listen for. The name of the coroutine will be used as the event name
        unless otherwise specified.

        .. code-block:: python3

            @client.event('on_request')
            async def on_request(response: aiohttp.ClientRequest):
                print('We requested something!', response.status)

        Parameters
        ----------
        event: Optional[:class:`str`]
            The event to listen for. If not provided, the name of the function will be used.

        Raises
        ------
        TypeError
            The function passed is not a coroutine.
        ValueError
            The event name does not start with ``on_``.
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

    def get_listeners(self, event: str) -> List[EventCoro[..., Any]]:
        """Retrieve all listeners that fall under the given event name.

        Parameters
        ----------
        event: :class:`str`
            The event to retrieve listeners for.

        Returns
        -------
        List[Union[Callable, :class:`asyncio.Future`]]
            A list of all listeners for the event. If the listener is of type :class:`asyncio.Future`,
            it was spawned from :meth:`wait_for`.
        """
        return self._listeners.get(event, [])

    def remove_listener(self, event: str, *, callback: Optional[EventCoro[P, T]] = None) -> None:
        """Removes a listener from the client via the event name and callback.

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

    @overload
    async def wait_for(
        self,
        event: Literal['request'],
        check: Optional[Callable[[aiohttp.ClientResponse], Optional[bool]]] = None,
        timeout: Optional[float] = None,
    ) -> aiohttp.ClientResponse:
        ...

    @overload
    async def wait_for(
        self, event: str, check: Optional[Callable[..., Optional[bool]]] = ..., timeout: Optional[float] = None
    ) -> Any:
        ...

    async def wait_for(
        self, event: str, check: Optional[Callable[..., Optional[bool]]] = None, timeout: Optional[float] = None
    ) -> Any:
        """|coro|

        Wait for a specific event to be dispatched, optionally checking for a condition
        to be met.

        This method returns a :class:`asyncio.Future` that you can await on. Note that if the event dispatched
        has kwargs, they will be passed to the check but not to the :class:`asyncio.Future` result.

        .. code-block:: python3

            def check(response: aiohttp.ClientResponse) -> bool:
                return response.status == 200

            response = await client.wait_for('request', check=check)

        Parameters
        ----------
        event: :class:`str`
            The event to wait for. Note the event passed here should not be prefixed
            with ``on_``, just the name of the event itself.
        check: Optional[Callable[..., Optional[bool]]]
            A predicate to check what to wait for. The arguments must match the parameters
            passed to the event being waited for.
        timeout: Optional[:class:`float`]
            The number of seconds to wait before timing out and raising :exc:`asyncio.TimeoutError`.

        Raises
        ------
        asyncio.TimeoutError
            The event was not dispatched in time and ``timeout`` was provided.
        RuntimeError
            This method was called from an OS thread that has no running event loop.
        """
        loop = asyncio.get_running_loop()

        future = loop.create_future()

        waiters = self._waiters.setdefault(f'on_{event}', [])
        waiters.append((future, check))

        return await asyncio.wait_for(
            future,
            timeout=timeout,
        )

    async def cleanup(self) -> None:
        """|coro|

        A helper cleanup the client's HTTP session. Internally,
        this is used in the context manager to cleanup the session, but can be used
        to manually cleanup the session if needed.
        """
        if not self._http.session:
            raise ValueError('No session to cleanup')

        await self._http.session.close()

    def get_user(self, id: str, /) -> Optional[User]:
        """Get a user from the internal cache of users.

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

    def get_domain(self, url: str, /) -> Optional[Domain]:
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
        """A method used to get a partial upload from its ID. This will
        create a partial upload object that can be used to delete the upload
        without having to fetch it.

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

        Fetches a user from the given ID.

        Parameters
        ----------
        id: :class:`str`
            The ID of the user to fetch.

        Returns
        -------
        :class:`User`
            The fetched user.

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

    async def upload(
        self,
        file: File,
        /,
        *,
        domain: Optional[Union[Domain, str]] = None,
        upload_type: UploadType = UploadType.public,
    ) -> Upload:
        """|coro|

        Upload a file to Tixte.

        Parameters
        ----------
        file: :class:`File`
            The file to upload. Please note :class:`discord.File` objects work as well.
        domain: Optional[Union[:class:`Domain`, :class:`str`]]
            Optionally, upload to a different domain than the client's default.
        upload_type: :class:`UploadType`
            Which type of upload to use. This can be either ``public`` or ``private``.

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
        data = await self._http.upload(file, domain=domain, upload_type=upload_type.value)
        return Upload(state=self._state, data=data)

    async def url_to_file(self, url: str, /, *, filename: Optional[str] = None) -> File:
        """|coro|

        Converts the given URL to a :class:`File` object. This will fetch the contents
        of the image URL, and then create a :class:`File` object with the contents.

        Parameters
        ----------
        url: :class:`str`
            The URL to convert.
        filename: Optional[:class:`str`]
            The filename to use for the file. Note that this must include the extension, such as
            ``some_file.png``. If this is ``None``, tixte will assume this to be a ``bin`` file.

        Returns
        -------
        :class:`File`
            The file with the given URL.
        """
        return await self._http.url_to_file(url=url, filename=filename)

    async def fetch_client_user(self) -> ClientUser:
        """|coro|

        Fetch the client's user. Once fetched for the first time, this can be accessed via the
        :attr:`user` attribute. Note that the client does not fetch this on login unless specifically requested
        via the :attr:`fetch_client_user_on_start` attribute is ``True`` and the client is run in a context manager setting.

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

        Fetch the configuration settings you have within Tixte.
        Those settings can be found on the Tixte website on the Embed Editor page,
        and the Page Design page within your Tixte dashboard.

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

        Creates a domain on Tixte.

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
