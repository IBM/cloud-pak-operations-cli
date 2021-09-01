from typing import Any, Final, Optional

from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from dg.lib.fyre.response_managers.default_response_manager import (
    DefaultResponseManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.types.default_success_response import DefaultSuccessResponse
from dg.utils.http_method import HTTPMethod


class OCPTransferPutManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str], cluster_name: str):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._cluster_name = cluster_name

    def execute_put_request(self, ocp_transfer_put_request: Any) -> DefaultSuccessResponse:
        return self._execute_request(HTTPMethod.PUT, ocp_transfer_put_request)

    # override
    def get_error_message(self) -> str:
        return "Failed to transfer OCP+ cluster"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return DefaultResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return {
            "additionalProperties": False,
            "properties": {
                "comment": {
                    "type": "string",
                },
                "new_owner": {
                    "type": "string",
                },
            },
            "required": [
                "new_owner",
            ],
            "type": "object",
        }

    # override
    def get_url(self) -> str:
        return OCPTransferPutManager._IBM_OCPPLUS_OCP_TRANSFER_PUT_URL.format(cluster_name=self._cluster_name)

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_TRANSFER_PUT_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}/transfer"
