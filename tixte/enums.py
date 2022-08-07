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

import enum

import enum_tools.documentation


@enum_tools.documentation.document_enum
class Region(enum.Enum):
    """Represents an upload region."""
    us_east_one = 'us-east-1' # doc: Represents the US East region.


@enum_tools.documentation.document_enum
class Premium(enum.Enum):
    """Represents the premium tiers of Tixte."""
    free = 0 # doc: The free tier. All default members have this tier.
    turbo = 1 # doc: Turbo tier. All members with this tier have an increased upload limit.
    turbo_charged = 2 # doc: Turbo charged tier. This is the highest tier. All members with this tier have an increased upload limit.


@enum_tools.documentation.document_enum
class UploadPermissionLevel(enum.Enum):
    """Represents an upload permission level. This level determines
    which members can view an upload.
    """
    viewer = 1 # doc: A viewer of this upload.
    manager = 2 # doc: A manager of this upload. Can manage viewers.
    owner = 3 # doc: The owner of this upload. Can manage everything.
