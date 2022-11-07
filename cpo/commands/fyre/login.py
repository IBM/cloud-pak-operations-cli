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

import cpo.config
import cpo.utils.network

from cpo.lib.fyre.ocp_plus_api_manager import OCPPlusAPIManager
from cpo.lib.fyre.utils.click import fyre_command_options
from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.logging import loglevel_command


@loglevel_command()
@fyre_command_options
def login(fyre_api_user_name: str, fyre_api_key: str, disable_strict_response_schema_check: bool):
    """Log in to Fyre"""

    credentials_to_be_stored = locals().copy()

    cpo.utils.network.disable_insecure_request_warning()

    try:
        OCPPlusAPIManager(fyre_api_user_name, fyre_api_key, disable_strict_response_schema_check).get_quota(None)
    except CloudPakOperationsCLIException as exception:
        if "failed authentication" in exception._error_message:
            raise CloudPakOperationsCLIException("Failed to log in to Fyre due to invalid credentials")
        else:
            raise CloudPakOperationsCLIException("Failed to log in to Fyre")

    cpo.config.configuration_manager.store_credentials(credentials_to_be_stored)
