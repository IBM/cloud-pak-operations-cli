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

from typing import List, TypedDict


class PlatformQuota(TypedDict):
    cpu_percent: int
    cpu_used: int  # optional
    cpu: str  # optional
    disk_percent: int
    disk_used: int  # optional
    disk: str  # optional
    memory_percent: int
    memory_used: int  # optional
    memory: str  # optional


class ProductGroupQuota(TypedDict):
    p: PlatformQuota
    product_group_id: str
    product_group_name: str
    x: PlatformQuota
    z: PlatformQuota


class QuotaGetResponse(TypedDict):
    details: List[ProductGroupQuota]
    status: str