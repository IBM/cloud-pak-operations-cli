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

from cpo.lib.error import DataGateCLIException
from cpo.lib.openshift.credentials.credentials import AbstractCredentials


class TokenCredentials(AbstractCredentials):
    def __init__(self, server: str, token: str, insecure_skip_tls_verify: bool):
        super().__init__(server, insecure_skip_tls_verify)
        self._token = token

    # override
    def get_access_token(self, force_refresh_if_possible: bool = False) -> str:
        return self._token

    # override
    def is_refreshable(self) -> bool:
        return False

    # override
    def persist_access_token(self, token: str):
        pass

    # override
    def refresh_access_token(self):
        raise DataGateCLIException("OAuth access token cannot be refreshed")
