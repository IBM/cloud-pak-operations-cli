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
import dg.lib.fyre.openshift
import dg.lib.openshift

from dg.lib.cluster.cluster import AbstractCluster, ClusterData


class FYRECluster(AbstractCluster):
    def __init__(self, server: str, cluster_data: ClusterData):
        super().__init__(server, cluster_data)

    def get_cluster_access_token(self) -> str:
        token = dg.lib.openshift.get_cluster_access_token(
            dg.lib.fyre.openshift.OPENSHIFT_OAUTH_AUTHORIZATION_ENDPOINT.format(
                self.cluster_data["cluster_name"]
            ),
            self.cluster_data["username"],
            self.cluster_data["password"],
        )

        return token

    def login(self):
        dg.lib.openshift.log_in_to_openshift_cluster_with_password(
            self.server, self.cluster_data["username"], self.cluster_data["password"]
        )
