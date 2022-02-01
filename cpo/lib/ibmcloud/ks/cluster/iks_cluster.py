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

from cpo.lib.cluster.cluster import AbstractCluster, ClusterData
from cpo.lib.ibmcloud import execute_ibmcloud_command


class IKSCluster(AbstractCluster):
    def __init__(self, server: str, cluster_data: ClusterData):
        super().__init__(server, cluster_data)

    # override
    def get_password(self) -> str:
        # TODO implement
        return ""

    # override
    def get_username(self) -> str:
        # TODO implement
        return ""

    # override
    def login(self):
        args = [
            "ks",
            "cluster",
            "config",
            "--cluster",
            self.get_cluster_data()["cluster_name"],
        ]

        execute_ibmcloud_command(args)
