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

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from .abc import Object
from .user import User, ClientUser
from .domain import Domain

if TYPE_CHECKING:
    from asyncio import Task

    from .http import HTTP
    from .client import Client

__all__: Tuple[str, ...] = ('State',)


class State(Object):
    if TYPE_CHECKING:
        _get_client: Callable[..., Client]

    def __init__(
        self,
        dispatch: Callable[..., List[Task[Any]]],
        http: HTTP,
        **kwargs: Any,
    ) -> None:
        self.dispatch: Callable[..., List[Task[Any]]] = dispatch
        self.http: HTTP = http
        self._maxsize: int = kwargs.get('maxsize', 1000)

        self._reload()

    def _reload(self) -> None:
        self.users: Dict[str, User] = {}
        self.client_user: Optional[ClientUser] = None
        self.domains: Dict[str, Domain] = {}

    def store_user(self, data: Any) -> User:
        user = User(state=self, data=data)
        self.users[user.id] = user
        return user

    def store_client_user(self, data: Any) -> ClientUser:
        user = ClientUser(state=self, data=data)
        self.client_user = user
        return user

    def remove_user(self, id: str) -> Optional[User]:
        return self.users.pop(id, None)

    def get_user(self, id: str) -> Optional[User]:
        return self.users.get(id)

    def store_domain(self, data: Any) -> Domain:
        domain = Domain(state=self, data=data)
        self.domains[domain.url] = domain
        return domain

    def remove_domain(self, url: str) -> Optional[Domain]:
        return self.domains.pop(url, None)

    def get_domain(self, url: str) -> Optional[Domain]:
        return self.domains.get(url)
