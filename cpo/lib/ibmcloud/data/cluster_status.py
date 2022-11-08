#  Copyright 2022 IBM Corporation
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

from typing import Any


class ClusterStatus:
    def __init__(self, status_output: Any):
        self._status_output = status_output

    def __str__(self) -> str:
        # TODO improve output
        return self.get_json()

    def get_json(self) -> str:
        return json.dumps(self._status_output, indent="\t", sort_keys=True)

    def get_server_url(self) -> str:
        return self._status_output["serverURL"] if "serverURL" in self._status_output else ""

    def has_name(self, name: str) -> bool:
        return ("name" in self._status_output) and (self._status_output["name"] == name)

    def is_ready(self) -> bool:
        result = False

        if (
            ("ingressHostname" in self._status_output)
            and (self._status_output["ingressHostname"] != "")
            and (self._status_output["masterHealth"] == "normal")
            and (self._status_output["masterState"] == "deployed")
            and (self._status_output["masterStatus"] == "Ready")
            and (self._status_output["state"] == "normal")
        ):
            result = True

        return result
