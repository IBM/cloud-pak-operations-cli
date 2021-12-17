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

from cpo.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.lib.fyre.response_managers.ocp_post_response_manager import (
    OCPPostResponseManager,
)
from cpo.lib.fyre.types.ocp_post_response import OCPPostResponse
from cpo.utils.http_method import HTTPMethod


class OCPDefaultPostManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str], platform: str):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._platform = platform

    def execute_post_request(self) -> OCPPostResponse:
        return self._execute_request(HTTPMethod.POST)

    # override
    def get_error_message(self) -> str:
        return "Failed to deploy OCP+ cluster"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPPostResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPDefaultPostManager._IBM_OCPPLUS_OCP_POST_DEFAULT_URL.format(platform=self._platform)

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_POST_DEFAULT_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/{platform}"
