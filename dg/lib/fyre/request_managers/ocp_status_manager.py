from typing import Any, Final, Optional

from dg.lib.fyre.data.status_data import OCPPlusClusterStatus
from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.response_managers.ocp_status_get_response_manager import (
    OCPStatusGetResponseManager,
)
from dg.utils.http_method import HTTPMethod


class OCPStatusManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str], cluster_name: str):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._cluster_name = cluster_name

    def execute_get_request(
        self,
    ) -> OCPPlusClusterStatus:
        return OCPPlusClusterStatus(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return "Failed to get OCP+ cluster status"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPStatusGetResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPStatusManager._IBM_OCPPLUS_OCP_STATUS_URL.format(cluster_name=self._cluster_name)

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_STATUS_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}/status"
