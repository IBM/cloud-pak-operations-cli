#  Copyright 2021, 2025 IBM Corporation
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

from cpo.lib.cluster.cluster import AbstractCluster, ClusterData
from cpo.lib.ibmcloud import INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY
from cpo.utils.error import CloudPakOperationsCLIException


class ROKSCluster(AbstractCluster):
    def __init__(self, server: str, cluster_data: ClusterData):
        super().__init__(server, cluster_data)

    # override
    def get_password(self) -> str:
        api_key = cpo.config.configuration_manager.get_value_from_credentials_file(
            INTERNAL_KEY_NAME_FOR_IBM_CLOUD_API_KEY
        )

        if api_key is None:
            credentials_file_path = cpo.config.configuration_manager.get_credentials_file_path()

            raise CloudPakOperationsCLIException(f"IBM Cloud API key not found in {credentials_file_path}")

        return api_key

    # override
    def get_username(self) -> str:
        return "apikey"
