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
from dg.utils.http_method import HTTPMethod


class OCPAddAdditionalNodesPutManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str], cluster_name: str):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

        self._cluster_name = cluster_name

    def execute_request_put_request(self, ocp_resource_put_request: Any):
        self._execute_request(HTTPMethod.PUT, ocp_resource_put_request)

    # override
    def get_error_message(self) -> str:
        return "Failed to add additional worker node"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return DefaultResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return {
            "additionalProperties": False,
            "properties": {
                "additional_disk": {
                    "items": {
                        "type": "string",
                    },
                    "type": "array",
                },
                "cpu": {
                    "type": "string",
                },
                "disable_scheduling": {
                    "type": "string",
                },
                "memory": {
                    "type": "string",
                },
                "site": {"type": "string"},
                "vm_count": {
                    "type": "string",
                },
            },
            "required": [
                "additional_disk",
            ],
            "type": "object",
        }

    # override
    def get_url(self) -> str:
        return OCPAddAdditionalNodesPutManager._IBM_OCPPLUS_OCP_ADD_ADDITIONAL_NODES_PUT_URL.format(
            cluster_name=self._cluster_name
        )

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_ADD_ADDITIONAL_NODES_PUT_URL: Final[
        str
    ] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}/add_additional_nodes"
