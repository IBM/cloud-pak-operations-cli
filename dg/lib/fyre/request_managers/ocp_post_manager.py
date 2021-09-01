from typing import Any, Final, Optional

from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.response_managers.ocp_post_response_manager import (
    OCPPostResponseManager,
)
from dg.lib.fyre.types.ocp_post_response import OCPPostResponse
from dg.utils.http_method import HTTPMethod


class OCPPostManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str]):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

    def execute_post_request(self, ocp_post_request: Any) -> OCPPostResponse:
        return self._execute_request(HTTPMethod.POST, ocp_post_request)

    # override
    def get_error_message(self) -> str:
        return "Failed to deploy OCP+ cluster"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return OCPPostResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return {
            "$defs": {
                "ha_proxy_timeout_data": {
                    "additionalProperties": False,
                    "properties": {
                        "check": {"type": "string"},
                        "client": {"type": "string"},
                        "connect": {"type": "string"},
                        "http-keep-alive": {"type": "string"},
                        "http-request": {"type": "string"},
                        "queue": {"type": "string"},
                        "server": {"type": "string"},
                    },
                    "type": "object",
                },
                "ha_proxy_data": {
                    "additionalProperties": False,
                    "properties": {
                        "timeout": {"$ref": "#/$defs/ha_proxy_timeout_data"},
                    },
                    "type": "object",
                },
                "worker_data": {
                    "additionalProperties": False,
                    "properties": {
                        "additional_disk": {
                            "items": {
                                "type": "string",
                            },
                            "type": "array",
                        },
                        "count": {"type": "string"},
                        "cpu": {"type": "string"},
                        "memory": {"type": "string"},
                    },
                    "required": [
                        "additional_disk",
                    ],
                    "type": "object",
                },
            },
            "additionalProperties": False,
            "properties": {
                "description": {"type": "string"},
                "expiration": {"type": "string"},
                "fips": {"type": "string"},
                "haproxy": {"$ref": "#/$defs/ha_proxy_data"},
                "name": {"type": "string"},
                "ocp_version": {"type": "string"},
                "platform": {"type": "string"},
                "product_group_id": {"type": "string"},
                "pull_secret": {"type": "string"},
                "quota_type": {"type": "string"},
                "site": {"type": "string"},
                "size": {"type": "string"},
                "ssh_key": {"type": "string"},
                "time_to_live": {"type": "string"},
                "worker": {
                    "items": {"$ref": "#/$defs/worker_data"},
                    "type": "array",
                },
            },
            "type": "object",
        }

    # override
    def get_url(self) -> str:
        return OCPPostManager._IBM_OCPPLUS_OCP_POST_URL

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_POST_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/ocp"
