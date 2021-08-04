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

from dg.config.cluster_credentials_manager import cluster_credentials_manager
from dg.lib.cluster.cluster import AbstractCluster
from dg.lib.openshift.credentials.user_credentials import UserCredentials


class ClusterBasedUserCredentials(UserCredentials):
    def __init__(self, cluster: AbstractCluster):
        super().__init__(cluster.get_server(), cluster.get_username(), cluster.get_password())

        self._cluster = cluster

    # override
    def get_access_token(self, force_refresh_if_possible: bool = False) -> str:
        if "token" not in self._cluster.get_cluster_data() or force_refresh_if_possible:
            self.refresh_access_token()

        return self._cluster.get_cluster_data()["token"]

    # override
    def persist_access_token(self, token: str):
        self._cluster = cluster_credentials_manager.edit_cluster(self._cluster.get_server(), {"token": token})
