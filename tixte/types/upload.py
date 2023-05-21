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

from typing import Optional, TypedDict, List
from typing_extensions import NotRequired

from .user import PartialUser


class UploadPermission(TypedDict):
    user: PartialUser

    # The API flip flops between access_level and permission_level
    access_level: NotRequired[int]
    permission_level: NotRequired[int]


class Upload(TypedDict):
    id: NotRequired[str]  # The API flip flops between id and asset_id
    asset_id: NotRequired[str]

    name: str
    region: str
    filename: str
    extension: str
    domain: str
    type: int
    expiration: Optional[str]
    permissions: List[UploadPermission]
    url: str
    dorect_url: str
    deletion_url: str
    message: str
    uploaded_at: NotRequired[str]


class BulkGetUploads(TypedDict):
    total: int
    results: int
    uploads: List[Upload]
