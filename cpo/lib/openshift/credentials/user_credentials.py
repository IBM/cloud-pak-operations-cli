#  Copyright 2021, 2022 IBM Corporation
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

import json
import urllib.parse

from typing import Final, Optional

import requests

from requests.models import Response

from cpo.lib.openshift.credentials.credentials import AbstractCredentials
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.network import ScopedInsecureRequestWarningDisabler


class UserCredentials(AbstractCredentials):
    OPENSHIFT_OAUTH_AUTHORIZATION_ENDPOINT: Final[
        str
    ] = "{authorization_endpoint}?client_id=openshift-challenging-client&response_type=token"

    def __init__(self, server: str, username: str, password: str, insecure_skip_tls_verify: bool):
        super().__init__(server, insecure_skip_tls_verify)
        self._password = password
        self._token: Optional[str] = None
        self._username = username

    # override
    def get_access_token(self, force_refresh_if_possible: bool = False) -> str:
        if self._token is None or force_refresh_if_possible:
            self.refresh_access_token()

        assert self._token is not None

        return self._token

    # override
    def is_refreshable(self) -> bool:
        return True

    # override
    def persist_access_token(self, token: str):
        self._token = token

    # override
    def refresh_access_token(self):
        authorization_endpoint = self._get_authorization_endpoint()
        response: Optional[Response] = None

        with ScopedInsecureRequestWarningDisabler(self._insecure_skip_tls_verify):
            response = requests.get(
                UserCredentials.OPENSHIFT_OAUTH_AUTHORIZATION_ENDPOINT.format(
                    authorization_endpoint=authorization_endpoint
                ),
                allow_redirects=False,
                auth=(self._username, self._password),
                verify=not self._insecure_skip_tls_verify,
            )

        if not response.ok:
            if response.content is not None:
                raise CloudPakOperationsCLIException(response.content.decode())
            else:
                response.raise_for_status()

        if "Location" not in response.headers:
            raise CloudPakOperationsCLIException("HTTP Location header not found")

        fragment = urllib.parse.parse_qs(urllib.parse.urlparse(response.headers["Location"]).fragment)

        if "access_token" not in fragment:
            raise CloudPakOperationsCLIException("access_token key not found in URL fragment")

        self.persist_access_token(fragment["access_token"][0])

    def _get_authorization_endpoint(self) -> str:
        """Returns the OAuth authorization endpoint returned by the OAuth server

        Returns
        -------
        str
            OAuth authorization endpoint returned by the OAuth server
        """

        response: Optional[Response] = None

        with ScopedInsecureRequestWarningDisabler(self._insecure_skip_tls_verify):
            response = requests.get(
                f"{self._server}/.well-known/oauth-authorization-server",
                verify=not self._insecure_skip_tls_verify,
            )

        if not response.ok:
            if response.content is not None:
                raise CloudPakOperationsCLIException(response.content.decode())
            else:
                response.raise_for_status()

        json_response = json.loads(response.content)

        if "authorization_endpoint" not in json_response:
            raise CloudPakOperationsCLIException("authorization_endpoint key not found in JSON response")

        authorization_endpoint = json_response["authorization_endpoint"]

        return authorization_endpoint
