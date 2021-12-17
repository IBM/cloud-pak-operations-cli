#  Copyright 2020, 2021 IBM Corporation
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

from pathlib import Path
from typing import Any

import cpo.lib.ibmcloud

from cpo.lib.error import DataGateCLIException
from cpo.lib.ibmcloud import execute_ibmcloud_command


def api_key_exists(name: str) -> bool:
    """Check if an API key exists"""

    api_keys = get_api_keys()
    result = False

    if api_keys:
        for api_key in api_keys:
            if api_key["name"] == name:
                result = True

                break

    return result


def delete_api_key_in_ibmcloud():
    execute_ibmcloud_command(
        [
            "iam",
            "api-key-delete",
            cpo.lib.ibmcloud.EXTERNAL_IBM_CLOUD_API_KEY_NAME,
            "--force",
        ]
    )


def generate_api_key() -> str:
    result = execute_ibmcloud_command(
        [
            "iam",
            "api-key-create",
            cpo.lib.ibmcloud.EXTERNAL_IBM_CLOUD_API_KEY_NAME,
            "--output",
            "json",
        ],
        capture_output=True,
    )

    return json.loads(result.stdout)["apikey"]


def get_api_keys() -> Any:
    result = execute_ibmcloud_command(["iam", "api-keys", "--output", "json"], capture_output=True)

    return json.loads(result.stdout)


def get_oauth_token() -> str:
    """Retrieves the IAM access token for the currently logged on user"""

    command = ["iam", "oauth-tokens", "--output", "json"]
    oauth_token_result = json.loads(execute_ibmcloud_command(command, capture_output=True).stdout)

    if oauth_token_result and "iam_token" in oauth_token_result:
        result = oauth_token_result["iam_token"]
    else:
        raise DataGateCLIException(f"Unable to retrieve oauth token using command '{command}'")

    return result


def get_tokens(api_key: str) -> Any:
    """Retrieves the IAM access token, refresh token and token type from the
    local ibmcloud configuration file"""

    bluemix_config_content = json.loads(Path(Path.home() / ".bluemix/config.json").read_text())
    split_iam_token = bluemix_config_content["IAMToken"].split()
    token_type = split_iam_token[0]
    access_token = split_iam_token[1]
    refresh_token = bluemix_config_content["IAMRefreshToken"]

    result = {
        "token_type": token_type,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    return result
