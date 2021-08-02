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

from typing import Dict, Any


class Config:
    """
    The base Config class you gget when using fetch_config.
    
    Attributes
    ----------
    custom_css: :class:`str`
        The custom CSS of your config
    hide_branding: :class:`bool`
        Whether or not you hide branding.
    base_redirect: :class:`bool`
        Whether or not you base redirect
    embed: :class:`dict`
        Your custom embed information.
    """
    def __init__(
        self, 
        status: Any,
        data: Dict
    ) -> None:
        self._status = status
        self._data = data
        
        self.custom_css: str = data['custom_css']
        self.hide_branding: bool = data['hide_branding']
        self.base_redirect: bool = data['base_redirect']
        self.embed: Dict = data['embed']
