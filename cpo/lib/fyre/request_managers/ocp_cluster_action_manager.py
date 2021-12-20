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
from cpo.lib.fyre.response_managers.default_response_manager import (
    DefaultResponseManager,
)
from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.utils.http_method import HTTPMethod


class OCPClusterActionManager(AbstractJSONRequestManager):
    def __init__(
        self,
        fyre_api_user_name: str,
        fyre_api_key: str,
        site: Optional[str],
        cluster_name: str,
        action: str,
    ):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._action = action
        self._cluster_name = cluster_name

    def execute_request_put_request(
        self,
    ):
        return self._execute_request(HTTPMethod.PUT)

    # override
    def get_error_message(self) -> str:
        return f"Failed to {self._action} cluster"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return DefaultResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPClusterActionManager._IBM_OCPPLUS_OCP_ACTION_PUT_URL.format(
            action=self._action, cluster_name=self._cluster_name
        )

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_ACTION_PUT_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}/{action}"
