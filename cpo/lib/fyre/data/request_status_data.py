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

from typing import List

import click

from tabulate import tabulate

from cpo.lib.fyre.types.ocp_request_get_response import OCPRequestGetResponse


class RequestStatusData:
    def __init__(self, ocp_request_get_response: OCPRequestGetResponse):
        self._ocp_request_get_response = ocp_request_get_response

    def format(self, use_json: bool = False):
        if use_json:
            click.echo(json.dumps(self._ocp_request_get_response, indent="\t", sort_keys=True))
        else:
            headers: List[str] = []
            tabular_data: List[str] = []

            for key in self._ocp_request_get_response["request"].keys():
                self._add_value(headers, tabular_data, key)

            click.echo(tabulate([tabular_data], headers))

    def get_status(self) -> OCPRequestGetResponse:
        return self._ocp_request_get_response

    def _add_value(self, headers: List[str], tabular_data: List[str], value: str):
        headers.append(value.replace("_", " "))
        value = str(self._ocp_request_get_response["request"][value])
        tabular_data.append(value)
