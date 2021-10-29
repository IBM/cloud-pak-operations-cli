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

from typing import List, Optional, TypedDict


class JobStatus(TypedDict):
    completion_percent: int
    status: str


class VM(TypedDict):
    job_status: JobStatus
    kvm_state: str
    name: str
    pingable_last_checked: Optional[str]
    pingable: str
    platform: str
    sshable_last_checked: str
    sshable: str
    state_last_checked: str
    state: str
    vm_id: str


class OCPStatusGetResponse(TypedDict):
    cluster_id: str
    cluster_name: str
    deployed_status: str
    expiration: str
    location_name: str
    product_group_id: str
    product_group: str
    status: str
    type: str
    vm_count: int
    vm: List[VM]
