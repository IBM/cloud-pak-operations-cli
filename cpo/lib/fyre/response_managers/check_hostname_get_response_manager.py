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

from typing import Any, Optional, Type

from cpo.lib.fyre.response_managers.json_response_manager import (
    AbstractJSONResponseManager,
)
from cpo.lib.fyre.types.check_hostname_get_response import (
    CheckHostnameGetResponse,
)


class CheckHostnameGetResponseManager(AbstractJSONResponseManager):
    """JSON response manager for check_hostname/{name} REST endpoint (GET)"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        return None

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return None

    # override
    def get_response_schema(self) -> Any:
        return {
            "additionalProperties": False,
            "properties": {
                "details": {
                    "type": "string",
                },
                "fqdn": {
                    "type": "string",
                },
                "last_used": {
                    "type": "string",
                },
                "name_id": {
                    "type": "string",
                },
                "names_id": {
                    "type": "string",
                },
                "owning_user": {
                    "type": "string",
                },
                "status": {
                    "type": "string",
                },
            },
            "required": [
                "details",
                "status",
            ],
            "type": "object",
        }

    # override
    def get_response_type(self) -> Type:
        return CheckHostnameGetResponse
