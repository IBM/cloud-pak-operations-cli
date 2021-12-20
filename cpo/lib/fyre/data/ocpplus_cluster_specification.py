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

import re as regex

from typing import List, Optional

from cpo.lib.error import DataGateCLIException
from cpo.lib.fyre.types.ocp_post_request import (
    HAProxyData,
    HAProxyTimeoutData,
    OCPPostRequest,
)
from cpo.utils.string import removeprefix


class HAProxyTimoutSettings:
    def __init__(
        self,
        check: Optional[str] = None,
        client: Optional[str] = None,
        connect: Optional[str] = None,
        http_keep_alive: Optional[str] = None,
        http_request: Optional[str] = None,
        queue: Optional[str] = None,
        server: Optional[str] = None,
    ):
        self.check = self._check_argument(check)
        self.client = self._check_argument(client)
        self.connect = self._check_argument(connect)
        self.http_keep_alive = self._check_argument(http_keep_alive)
        self.http_request = self._check_argument(http_request)
        self.queue = self._check_argument(queue)
        self.server = self._check_argument(server)

    def add_settings_to_dict(self, ocp_request: OCPPostRequest):
        timeout_dict: HAProxyTimeoutData = {}

        for name in dir(self):
            value = getattr(self, name)

            if not name.startswith("__") and not callable(getattr(self, name)) and value is not None:
                timeout_dict[removeprefix(name, "_").replace("_", "-")] = value

        haproxy_dict: HAProxyData = {"timeout": timeout_dict}

        if len(timeout_dict) != 0:
            ocp_request["haproxy"] = haproxy_dict

    def _check_argument(self, argument: Optional[str]) -> Optional[str]:
        if argument is not None:
            search_result = regex.match("\\d+[d|h|m|ms|s|us]", argument)

            if search_result is None:
                raise DataGateCLIException(f"Invalid string format: {argument}")

        return argument


class QuickBurnSettings:
    def __init__(self, quick_burn_size: str, quick_burn_time_to_live: int):
        self.quick_burn_size = quick_burn_size
        self.quick_burn_time_to_live = quick_burn_time_to_live


class WorkerNodeSettings:
    def __init__(
        self,
        worker_node_additional_disk_size: List[int],
        worker_node_count: Optional[int] = None,
        worker_node_num_cpus: Optional[int] = None,
        worker_node_ram_size: Optional[int] = None,
    ):
        self.worker_node_additional_disk_size = worker_node_additional_disk_size
        self.worker_node_count = worker_node_count
        self.worker_node_num_cpus = worker_node_num_cpus
        self.worker_node_ram_size = worker_node_ram_size

    def worker_settings_exist(self) -> bool:
        return any(
            [
                len(self.worker_node_additional_disk_size) != 0,
                self.worker_node_count is not None,
                self.worker_node_num_cpus is not None,
                self.worker_node_ram_size is not None,
            ]
        )


class OCPPlusClusterSpecification:
    def __init__(
        self,
        alias: Optional[str],
        name: Optional[str],
        description: Optional[str] = None,
        expiration: Optional[int] = None,
        fips: bool = False,
        haproxy_timeout_settings: Optional[HAProxyTimoutSettings] = None,
        ocp_version: Optional[str] = None,
        platform: Optional[str] = None,
        product_group_id: Optional[int] = None,
        pull_secret: Optional[str] = None,
        quick_burn_settings: Optional[QuickBurnSettings] = None,
        ssh_key: Optional[str] = None,
        worker_node_settings: Optional[WorkerNodeSettings] = None,
    ):
        """Constructor

        Parameters
        ----------
        alias
            alias used to reference a cluster instead of its server URL
        name
            cluster name
        description
            cluster description
        expiration
            cluster expiration (hours)
        fips
            flag indicating whether FIPS encryption shall be enabled
        haproxy_timeout_settings
            HAProxy timeout settings
        ocp_version
            OpenShift version
        platform
            Hardware platform
        product_group_id
            FYRE product group ID
        pull_secret
            Pull secret
        quick_burn_settings
            Quick burn settings
        ssh_key
            SSH key
        worker_node_settings
            worker node settings
        """

        self.alias = alias
        self.description = description
        self.expiration = expiration
        self.fips = fips
        self.haproxy_timeout_settings = haproxy_timeout_settings
        self.name = name
        self.ocp_version = ocp_version
        self.platform = platform
        self.product_group_id = product_group_id
        self.pull_secret = pull_secret
        self.quick_burn_settings = quick_burn_settings
        self.ssh_key = ssh_key
        self.worker_node_settings = worker_node_settings

    def worker_settings_exist(self) -> bool:
        return self.worker_node_settings is not None and self.worker_node_settings.worker_settings_exist()
