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

from typing import Optional, TypedDict

from cpo.lib.fyre.types.shared import IP


class VM(TypedDict):
    additional_disk: list[str]
    cpu: str
    hostname: str
    ips: list[IP]
    memory: str
    os_disk: str
    os_state: str
    pingable_last_checked: Optional[str]
    pingable: str
    vm_id: str


class Cluster(TypedDict):
    access_url: str
    auto_patch: str
    cluster_count: str
    cluster_id: str
    cluster_name: str
    cluster_type: str
    compliance: str
    created: str
    deployment_status: str
    description: str
    expiration: str
    fips_enabled: str
    kubeadmin_password: str
    location_name: str
    locked_for_delete: str
    ocp_username: str
    ocp_version: str
    product_group: str
    product_group_id: str
    vm_count: int
    vms: list[VM]


class OCPGetResponse(TypedDict):
    cluster_count: int
    clusters: list[Cluster]
    details: str
    status: str
