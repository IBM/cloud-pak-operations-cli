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


class OCPNodeActionManager(AbstractJSONRequestManager):
    def __init__(
        self,
        fyre_user_name: str,
        fyre_api_key: str,
        site: Optional[str],
        cluster_name: str,
        node_name: str,
        action: str,
    ):
        super().__init__(fyre_user_name, fyre_api_key, site)

        self._action = action
        self._cluster_name = cluster_name
        self._node_name = node_name

    def execute_request_put_request(
        self,
    ):
        return self._execute_request(HTTPMethod.PUT)

    # override
    def get_error_message(self) -> str:
        return f"Failed to {self._action} node"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return DefaultResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return OCPNodeActionManager._IBM_OCPPLUS_OCP_ACTION_NODE_PUT_URL.format(
            action=self._action, cluster_name=self._cluster_name, node_name=self._node_name
        )

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_OCP_ACTION_NODE_PUT_URL: Final[
        str
    ] = "https://ocpapi.svl.ibm.com/v1/ocp/{cluster_name}/{node_name}/{action}"