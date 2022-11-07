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

from cpo.lib.ibmcloud.ibm_cloud_api_manager import IBMCloudAPIManager
from cpo.utils.logging import loglevel_command


@loglevel_command()
def regenerate_api_key():
    """Deletes the current IBM Cloud API key and generates a new one"""

    ibm_cloud_api_manager = IBMCloudAPIManager()
    ibm_cloud_api_manager.regenerate_api_key()
