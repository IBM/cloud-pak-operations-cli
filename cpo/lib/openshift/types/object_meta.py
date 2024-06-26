#  Copyright 2021, 2024 IBM Corporation
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


class ObjectMetaOptional(TypedDict, total=False):
    creationTimestamp: str | None
    labels: dict[str, str]
    namespace: str


class ObjectMetaRequired(TypedDict):
    name: str


class ObjectMeta(ObjectMetaOptional, ObjectMetaRequired, total=False):
    """
    Notes
    -----
    https://docs.openshift.com/container-platform/latest/rest_api/objects/index.html#objectmeta_v2-meta-v1"""
