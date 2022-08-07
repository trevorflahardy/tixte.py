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

from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union

from .abc import Object

if TYPE_CHECKING:
    from aiohttp import ClientResponse

__all__: Tuple[str, ...] = (
    'TixteException',
    'HTTPException',
    'NotFound',
    'Forbidden',
    'TixteServerError',
    'PaymentRequired',
)


class TixteException(Exception, Object):
    """The base Tixte Exception. All Tixte Exceptions inherit from this."""

    __slots__: Tuple[str, ...] = ()


class HTTPException(TixteException):
    """An exception raised when an HTTP Exception occurs from the API.

    Attributes
    ----------
    response: :class:`aiohttp.ClientResponse`
        The response from the API.
    data: :class:`Any`
        The data returned from the API.
    """

    __slots__: Tuple[str, ...] = (
        'response',
        'data',
    )

    def __init__(
        self,
        response: Optional[ClientResponse] = None,
        data: Optional[Union[Dict[Any, Any], Any]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.response: Optional[ClientResponse] = response
        self.data: Any = data

        self.message: Optional[str]
        self.code: Optional[str]

        if isinstance(data, dict):
            self.message = data.get('error', {}).get('message')
            self.code = data.get('error', {}).get('code')
        else:
            self.message = None
            self.code = None

        message_fmt = f'{self.code or "No code."}: {self.message or "No message"}.'
        super().__init__(message_fmt, *args, **kwargs)


class NotFound(HTTPException):
    """An exception raised when an object is not Found.

    This inherits from :class:`HTTPException`.
    """

    __slots__: Tuple[str, ...] = ()


class Forbidden(HTTPException):
    """An exception raised when the user does not have permission
    to perform an action.

    This inherits from :class:`HTTPException`.
    """

    __slots__: Tuple[str, ...] = ()


class TixteServerError(HTTPException):
    """An exception raised when an internal Tixte server error
    occurs from the API.

    This inherits from :class:`HTTPException`.
    """

    __slots__: Tuple[str, ...] = ()


class PaymentRequired(HTTPException):
    """An exception raised when you attempt to perform an operation
    on your account with the wrong payment tier.

    This inherits from :class:`HTTPException`.
    """

    __slots__: Tuple[str, ...] = ()
