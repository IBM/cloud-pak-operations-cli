#  Copyright 2021, 2023 IBM Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import TypedDict

from cpo.lib.fyre.types.default_success_response import DefaultSuccessResponse


class Error(TypedDict):
    error: str
    issued: str


class Details(TypedDict):
    errors: list[Error | str]


class OCPPostErrorResponseOptional(TypedDict, total=False):
    build_errors: list[str]


class OCPPostErrorResponse(OCPPostErrorResponseOptional):
    details: Details | str
    status: str


class OCPPostResponse(DefaultSuccessResponse):
    cluster_name: str
