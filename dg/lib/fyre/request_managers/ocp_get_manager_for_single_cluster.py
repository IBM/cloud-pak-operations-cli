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

from typing import Any, Final, Optional

from dg.lib.fyre.data.ocpplus_cluster import OCPPlusCluster
from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.response_managers.ocp_get_response_manager_for_single_cluster import (
    OCPGetResponseManagerForSingleCluster,
)
from dg.utils.http_method import HTTPMethod


class OCPGetManagerForSingleCluster(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str], cluster_name: str):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._cluster_name = cluster_name

    def execute_get_request(
        self,
    ) -> OCPPlusCluster:
        return OCPPlusCluster(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return "Failed to get OCP+ cluster details"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPGetResponseManagerForSingleCluster()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPGetManagerForSingleCluster._IBM_OCPPLUS_OCP_GET_URL_FOR_SINGLE_CLUSTER.format(
            cluster_name=self._cluster_name
        )

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_GET_URL_FOR_SINGLE_CLUSTER: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}"
