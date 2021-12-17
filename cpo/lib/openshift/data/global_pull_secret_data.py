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

import base64
import json
import re as regex

from typing import Any, List, Optional

import click
import jmespath

from tabulate import tabulate

from cpo.lib.error import (
    DataGateCLIException,
    JmespathPathExpressionNotFoundException,
    UnexpectedTypeException,
)
from cpo.lib.openshift.types.auths_dict import AuthDict, AuthsDict
from cpo.lib.openshift.types.credentials import Credentials


class GlobalPullSecretData:
    """Manages the global pull secret"""

    def __init__(self, data: Any):
        expression = '".dockerconfigjson"'
        search_result = jmespath.search(expression, data)

        if search_result is None:
            raise JmespathPathExpressionNotFoundException(expression)

        if not isinstance(search_result, str):
            raise UnexpectedTypeException(search_result)

        self._secret_get_response: AuthsDict = json.loads(base64.standard_b64decode(search_result))

    def contains(self, registry_location: str) -> bool:
        """Returns whether the global pull secret contains credentials for the
        given registry location

        Parameters
        ----------
        registry_location
            registry location to be searched for

        Returns
        -------
        bool
            true, if the global pull secret contains credentials for the given
            registry location
        """

        return jmespath.search(f'auths."{registry_location}".auth', self._secret_get_response) is not None

    def delete_credentials(self, registry_location: str):
        """Deletes credentials for the given registry location from the global
        pull secret

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be deleted
        """

        auths = self._secret_get_response["auths"]

        if registry_location not in auths:
            raise DataGateCLIException(f"Credentials for registry location '{registry_location}' not found")

        del auths[registry_location]

        self._secret_get_response["auths"] = dict(sorted(auths.items(), key=lambda auth: auth[0]))

    def format(self, use_json: bool = False):
        """Prints registry credentials stored in the global pull secret

        Parameters
        ----------
        use_json
            flag indicating whether the JSON response of the OpenShift server shall
            be printed
        """

        if use_json:
            click.echo(json.dumps(self._secret_get_response, indent="\t", sort_keys=True))
        else:
            auth_list: List[List[str]] = []
            auths = self._secret_get_response["auths"]

            for image_registry, auth in auths.items():
                search_result = regex.match("(.*)\\:(.*)", base64.standard_b64decode(auth["auth"]).decode("utf-8"))

                if search_result is None:
                    raise DataGateCLIException("…")

                image_registry_password = search_result.group(2)

                if len(image_registry_password) > 5:
                    image_registry_password = image_registry_password[0:5] + "…"

                auth_list_element: List[str] = [image_registry, search_result.group(1), image_registry_password]

                auth_list.append(auth_list_element)

            auth_list.sort(key=lambda auth_list_element: auth_list_element[0])
            click.echo(tabulate(auth_list, headers=["registry location", "username", "password"]))

    def get_credentials(self, registry_location: str) -> Optional[Credentials]:
        """Returns credentials for the given registry location

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be returned

        Returns
        -------
        str
            credentials for the given registry location
        """

        search_result: Any = jmespath.search(f'auths."{registry_location}".auth', self._secret_get_response)

        return self._decode_credentials(search_result) if search_result is not None else None

    def get_json_patch(self) -> Any:
        """Returns the global pull secret as a JSON Patch object

        Notes
        -----
        http://jsonpatch.com

        Returns
        -------
        Any
            global pull secret as a JSON Patch object
        """

        return [
            {
                "op": "replace",
                "path": "/data/.dockerconfigjson",
                "value": base64.standard_b64encode(json.dumps(self._secret_get_response).encode()).decode("utf-8"),
            }
        ]

    def set_credentials(self, registry_location: str, username: str, password: str):
        """Sets credentials for the given registry location

        Parameters
        ----------
        registry_location
            registry location for which credentials shall be set
        username
            registry location username
        password
            registry location password
        """

        auth: AuthDict = {"auth": base64.standard_b64encode(f"{username}:{password}".encode()).decode("utf-8")}

        auths = self._secret_get_response["auths"]
        auths[registry_location] = auth

        self._secret_get_response["auths"] = dict(sorted(auths.items(), key=lambda auth: auth[0]))

    def _decode_credentials(self, encoded_credentials: str) -> Credentials:
        """Decodes Base64-encoded credentials

        Parameters
        ----------
        encoded_credentials
            Base64-encoded credentials

        Returns
        -------
        Credentials
            Base64-decoded credentials (username, password)
        """

        search_result = regex.match("(.*)\\:(.*)", base64.standard_b64decode(encoded_credentials).decode("utf-8"))

        if search_result is None:
            raise DataGateCLIException("Invalid credentials format")

        return Credentials(username=search_result.group(1), password=search_result.group(2))
