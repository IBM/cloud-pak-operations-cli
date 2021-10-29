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

HAProxyTimeoutData = TypedDict(
    "HAProxyTimeoutData",
    {
        "check": str,
        "client": str,
        "connect": str,
        "http-keep-alive": str,
        "http-request": str,
        "queue": str,
        "server": str,
    },
    total=False,
)

HAProxyData = TypedDict("HAProxyData", {"timeout": HAProxyTimeoutData})


class WorkerData(TypedDict, total=False):
    additional_disk: List[str]
    count: str
    cpu: str
    memory: str


class OCPPostRequest(TypedDict, total=False):
    description: str
    expiration: str
    fips: str
    haproxy: HAProxyData
    name: str
    ocp_version: str
    platform: str
    product_group_id: str
    pull_secret: str
    quota_type: str
    site: str
    size: str
    ssh_key: str
    time_to_live: str
    worker: List[WorkerData]
