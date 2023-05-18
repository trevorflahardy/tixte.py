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

from typing import NamedTuple

__version__ = '1.0.2'
__author__ = 'NextChai'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2021-present NextChai'

from . import abc as abc, utils as utils
from .client import *
from .config import *
from .delete import *
from .domain import *
from .enums import *
from .errors import *
from .file import *
from .permissions import *
from .upload import *
from .user import *


class VersionInfo(NamedTuple):
    major: int
    minor: int
    micro: int
    releaselevel: str
    serial: int


version_info = VersionInfo(0, 0, 6, 'final', 0)
