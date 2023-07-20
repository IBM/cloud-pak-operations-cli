#  Copyright 2021, 2023 IBM Corporation
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

from typing import Any

from cpo.lib.ibmcloud.ibm_cloud_api_manager import IBMCloudAPIManager


def list_existing_clusters(json: bool) -> str | Any:
    """List all available clusters"""

    args = ["oc", "cluster", "ls"]

    if json:
        args.append("--json")

    result = IBMCloudAPIManager().execute_ibmcloud_command(args, capture_output=True)

    return result.stdout
