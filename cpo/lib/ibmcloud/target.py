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

from typing import Any

from cpo.lib.ibmcloud import execute_ibmcloud_command


def get_ibmcloud_account_target_information() -> Any:
    """Get the targeted region, account, resource group, org or space"""

    args = ["target", "--output", "json"]
    result = execute_ibmcloud_command(args, capture_output=True)
    result_json = json.loads(result.stdout)

    return result_json
