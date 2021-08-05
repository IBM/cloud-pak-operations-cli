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

import dg.config
import dg.lib.ibmcloud
import dg.lib.openshift.oc

from dg.lib.cluster.cluster import AbstractCluster, ClusterData
from dg.lib.error import DataGateCLIException
from dg.lib.ibmcloud import INTERNAL_IBM_CLOUD_API_KEY_NAME


class ROKSCluster(AbstractCluster):
    def __init__(self, server: str, cluster_data: ClusterData):
        super().__init__(server, cluster_data)

    def get_password(self) -> str:
        api_key = dg.config.data_gate_configuration_manager.get_value_from_credentials_file(
            INTERNAL_IBM_CLOUD_API_KEY_NAME
        )

        if api_key is None:
            credentials_file_path = dg.config.data_gate_configuration_manager.get_dg_credentials_file_path()

            raise DataGateCLIException(f"IBM Cloud API key not found in {credentials_file_path}")

        return api_key

    def get_username(self) -> str:
        return "apikey"

    def login(self):
        api_key = dg.config.data_gate_configuration_manager.get_value_from_credentials_file(
            dg.lib.ibmcloud.INTERNAL_IBM_CLOUD_API_KEY_NAME
        )

        if api_key is None:
            raise DataGateCLIException("IBM Cloud API key not found in stored credentials")

        dg.lib.openshift.oc.log_in_to_openshift_cluster_with_password(self.server, "apikey", api_key)
