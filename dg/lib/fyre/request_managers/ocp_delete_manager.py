from typing import Any, Final, Optional

from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
    HTTPMethod,
)
from dg.lib.fyre.response_managers.default_response_manager import (
    DefaultResponseManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.types.default_success_response import DefaultSuccessResponse


class OCPDeleteManager(AbstractJSONRequestManager):
    def __init__(self, fyre_user_name: str, fyre_api_key: str, site: Optional[str], cluster_name: str):
        super().__init__(fyre_user_name, fyre_api_key, site)

        self._cluster_name = cluster_name

    def execute_delete_request(self) -> DefaultSuccessResponse:
        return self._execute_request(HTTPMethod.DELETE)

    # override
    def get_error_message(self) -> str:
        return "Failed to delete OCP+ cluster"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return DefaultResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPDeleteManager._IBM_OCPPLUS_OCP_DELETE_URL.format(cluster_name=self._cluster_name)

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_DELETE_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}"