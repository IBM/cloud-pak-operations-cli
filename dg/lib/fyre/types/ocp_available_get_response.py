#  Copyright 2021 IBM Corporation
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

from typing import List, TypedDict


class NodeSize(TypedDict):
    additional_disk_size: str
    additional_disk: str
    base_disk_size: str
    count: str
    cpu: str
    max_cpu: str
    max_disk_size: str
    max_disk: str
    max_memory: str
    memory: str


class DefaultClusterSizeData(TypedDict):
    inf: NodeSize
    master: NodeSize
    worker: NodeSize


class OCPAvailableGetResponse(TypedDict):
    default_size: DefaultClusterSizeData
    ocp_versions: List[str]
