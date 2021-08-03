from typing import Any, Final, Optional

from dg.lib.fyre.data.product_group_quota_data import ProductGroupQuotaData
from dg.lib.fyre.request_managers.json_request_manager import (
    AbstractJSONRequestManager,
)
from dg.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from dg.lib.fyre.response_managers.quota_get_response_manager import (
    QuotaGetResponseManager,
)
from dg.utils.http_method import HTTPMethod


class QuotaRequestManager(AbstractJSONRequestManager):
    def __init__(self, fyre_api_user_name: str, fyre_api_key: str, site: Optional[str] = None):
        super().__init__(fyre_api_user_name, fyre_api_key, site)

    def execute_get_request(
        self,
    ) -> ProductGroupQuotaData:
        return ProductGroupQuotaData(self._execute_request(HTTPMethod.GET))

    # override
    def get_error_message(self) -> str:
        return "Failed to get all quotas for product groups the current user is part of"

    # override
    def get_json_response_manager(self) -> AbstractJSONResponseManager:
        return QuotaGetResponseManager()

    # override
    def get_request_schema(self) -> Any:
        return self.get_default_request_schema()

    # override
    def get_url(self) -> str:
        return self._IBM_OCPPLUS_QUOTA_GET_URL

    # override
    def is_request_id_to_be_ignored(self) -> bool:
        return False

    _IBM_OCPPLUS_QUOTA_GET_URL: Final[str] = "https://ocpapi.svl.ibm.com/v1/quota"
