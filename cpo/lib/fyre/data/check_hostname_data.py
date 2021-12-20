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

import json

import click

from cpo.lib.fyre.types.check_hostname_get_response import (
    CheckHostnameGetResponse,
)


class CheckHostNameData:
    def __init__(self, cluster_name: str, check_hostname_get_response: CheckHostnameGetResponse):
        self._check_hostname_get_response = check_hostname_get_response
        self._cluster_name = cluster_name

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._check_hostname_get_response, indent="\t", sort_keys=True))
        else:
            if self._check_hostname_get_response["status"] == "warning":
                message = f"Hostname {self._cluster_name}.cp.fyre.ibm.com is not available"

                if "owning_user" in self._check_hostname_get_response:
                    owning_user = self._check_hostname_get_response["owning_user"]

                    if "name_id" in self._check_hostname_get_response:
                        name_id = self._check_hostname_get_response["name_id"]

                        message += f" (owning user: {owning_user}/name ID: {name_id})"
                    else:
                        message += f" (owning user: {owning_user})"

                click.echo(message + ".")
            else:
                click.echo(f"Hostname {self._cluster_name}.cp.fyre.ibm.com is available.")
