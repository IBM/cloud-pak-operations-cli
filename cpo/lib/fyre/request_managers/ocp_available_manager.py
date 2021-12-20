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

from cpo.lib.fyre.data.ocp_available_data import OCPAvailableData
from cpo.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.lib.fyre.response_managers.ocp_available_get_response_manager import (
    OCPAvailableGetResponseManager,
)
from cpo.utils.http_method import HTTPMethod


class OCPAvailableManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str], platform: str):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._platform = platform

    def execute_get_request(
        self,
    ) -> OCPAvailableData:
        return OCPAvailableData(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return "Failed to get available OpenShift Container Platform versions/default sizes"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPAvailableGetResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    # override
    def get_url(self) -> str:
        return OCPAvailableManager._IBM_OCPPLUS_OCP_AVAILABLE_GET_URL.format(platform=self._platform)

    _IBM_OCPPLUS_OCP_AVAILABLE_GET_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp_available/{platform}"
