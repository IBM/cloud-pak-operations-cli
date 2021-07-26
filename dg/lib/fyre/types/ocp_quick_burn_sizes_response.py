#  Copyright 2020 IBM Corporation
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


class NodeSizeSpecification(TypedDict):
    additional_disk: str
    additional_disk_size: str
    count: str
    cpu: str
    disk_size: str
    memory: str


class NodeSizeSpecificationData(TypedDict):
    inf: NodeSizeSpecification
    master: NodeSizeSpecification
    worker: NodeSizeSpecification


class PlatformQuickBurnSizeSpecificationData(TypedDict):
    large: NodeSizeSpecificationData
    medium: NodeSizeSpecificationData


class OCPQuickBurnSizesResponse(TypedDict):
    p: PlatformQuickBurnSizeSpecificationData
    x: PlatformQuickBurnSizeSpecificationData
