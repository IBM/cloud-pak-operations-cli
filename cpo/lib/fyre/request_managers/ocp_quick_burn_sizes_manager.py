#  Copyright 2021, 2022 IBM Corporation
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

from cpo.lib.fyre.data.quick_burn_size_data import QuickBurnSizeData
from cpo.lib.fyre.request_managers.json_request_manager import AbstractJSONRequestManager
from cpo.lib.fyre.response_managers.json_response_manager import AbstractJSONResponseManager
from cpo.lib.fyre.response_managers.ocp_quick_burn_sizes_response_manager import OCPQuickBurnSizesResponseManager
from cpo.utils.http_method import HTTPMethod


class OCPQuickBurnSizesManager(AbstractJSONRequestManager):
    def __init__(
        self,
        fyre_api_user_name: str,
        fyre_api_key: str,
        disable_strict_response_schema_check: bool,
        site: Optional[str],
    ):
        super().__init__(fyre_api_user_name, fyre_api_key, disable_strict_response_schema_check, site)

    def execute_get_request(
        self,
    ) -> QuickBurnSizeData:
        return QuickBurnSizeData(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return "Failed to get available sizes for a quick burn deployment"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPQuickBurnSizesResponseManager(self._disable_strict_response_schema_check)

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPQuickBurnSizesManager._IBM_OCPPLUS_QUICK_BURN_SIZES_GET_URL

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_QUICK_BURN_SIZES_GET_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/quick_burn_sizes"
