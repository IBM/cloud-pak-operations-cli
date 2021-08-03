from typing import Any, Final, Optional

from dg.lib.fyre.data.quick_burn_size_data import QuickBurnSizeData
from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.response_managers.ocp_quick_burn_sizes_response_manager import (
    OCPQuickBurnSizesResponseManager,
)
from dg.utils.http_method import HTTPMethod


class OCPQuickBurnSizesManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str]):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

    def execute_get_request(
        self,
    ) -> QuickBurnSizeData:
        return QuickBurnSizeData(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return "Failed to get available sizes for a quick burn deployment"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPQuickBurnSizesResponseManager()

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
