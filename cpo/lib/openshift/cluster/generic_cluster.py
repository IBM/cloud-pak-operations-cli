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

import cpo.lib.openshift.oc

from cpo.lib.cluster.cluster import AbstractCluster, ClusterData


class GenericCluster(AbstractCluster):
    def __init__(self, server: str, cluster_data: ClusterData):
        super().__init__(server, cluster_data)

    def get_password(self) -> str:
        return self.cluster_data["password"]

    def get_username(self) -> str:
        return self.cluster_data["username"]

    # override
    def login(self):
        cpo.lib.openshift.oc.log_in_to_openshift_cluster_with_password(
            self.server, self.cluster_data["username"], self.cluster_data["password"]
        )
