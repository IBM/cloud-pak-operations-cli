#  Copyright 2020 IBM Corporation
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

from typing import Any, Union

from dg.commands.ibmcloud.common import is_logged_in
from dg.lib.thirdparty import execute_ibmcloud_command


def list_existing_clusters(json: bool) -> Union[str, Any]:
    """List all available clusters"""

    if not is_logged_in():
        raise Exception(
            "Not logged in to IBM Cloud. Please run 'dg ibmcloud login' to log in."
        )

    command = ["oc", "cluster", "ls"]
    if json:
        command.append("--json")

    result = execute_ibmcloud_command(command)

    if result.returncode != 0 and "ibmcloud login" in result.stderr:
        raise Exception("Please use 'dg ibmcloud login' before running this command.")

    return result.stdout
