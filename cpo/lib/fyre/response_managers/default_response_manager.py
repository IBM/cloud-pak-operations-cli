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
from cpo.lib.fyre.types.default_success_response import DefaultSuccessResponse


class DefaultResponseManager(AbstractJSONResponseManager):
    """JSON response manager for REST endpoints (PUT) returning a generic
    success response"""

    # override
    def get_error_message(self, json_error_response: Any) -> Optional[str]:
        return self.get_default_error_message(json_error_response)

    # override
    def get_error_response_schema(self) -> Optional[Any]:
        return self.get_default_error_response_schema()

    # override
    def get_response_schema(self) -> Any:
        return self.get_default_success_response_schema()

    # override
    def get_response_type(self) -> Type:
        return DefaultSuccessResponse
