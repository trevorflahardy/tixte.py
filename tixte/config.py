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

from typing import TYPE_CHECKING, Dict, Any, Mapping, Protocol, Tuple, Type
from typing_extensions import Self

from .abc import Object

if TYPE_CHECKING:
    from .state import State

__all__: Tuple[str, ...] = ('Config',)


class EmbedProtocol(Protocol):
    @classmethod
    def from_dict(cls: Type[Self], data: Mapping[str, Any]) -> Self:
        ...


class Config(Object):
    """
    The base Config class you gget when using get_config.

    Attributes
    ----------
    custom_css: :class:`str`
        The custom CSS of your config
    hide_branding: :class:`bool`
        Whether or not you hide branding.
    base_redirect: :class:`bool`
        Whether or not you base redirect
    """

    __slots__: Tuple[str, ...] = (
        '_state',
        'custom_css',
        'hide_branding',
        'base_redirect',
        '_embed',
    )

    def __init__(self, *, state: State, data: Dict[Any, Any]) -> None:
        self._state = state

        self.custom_css: str = data['custom_css']
        self.hide_branding: bool = data['hide_branding']
        self.base_redirect: bool = data['base_redirect']
        self._embed: Dict[Any, Any] = data['embed']

    def __repr__(self) -> str:
        return '<Config custom_css={0.custom_css} hide_branding={0.hide_branding} base_redirect={0.base_redirect}>'.format(
            self
        )

    @property
    def embed(self) -> Dict[str, Any]:
        """Dict[:class:`str`, Any]: Returns a formatted dictionary representing your embed from the embed editor."""
        embed = self._embed

        return {
            'title': embed.get('title'),
            'description': embed.get('description'),
            'author': {
                'name': embed.get('author_name'),
                'url': embed.get('author_url'),
            },
            'color': int(f'0x{color[1:]}', 16) if (color := embed.get('theme_color')) else 0x5865F2,
            'provider': {
                'name': embed.get('provider_name'),
                'url': embed.get('provider_url'),
            },
        }

    def to_embed(self, embed_cls: Type[EmbedProtocol]) -> EmbedProtocol:
        """
        Returns an instance of your embed class from the embed editor.

        Parameters
        ----------
        embed_cls: :class:`EmbedProtocol`
            The embed class you want to use. Must implement
            a ``from_dict`` classmethod.

        Returns
        -------
        Any
            An instance of your embed class.
        """
        return embed_cls.from_dict(self.embed)
