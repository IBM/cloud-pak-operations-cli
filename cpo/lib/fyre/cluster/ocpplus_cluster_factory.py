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

from cpo.lib.cluster.cluster import AbstractCluster
from cpo.lib.cluster.cluster_factory import AbstractClusterFactory, ClusterData
from cpo.lib.fyre.cluster.ocpplus_cluster import OCPPlusCluster


class OCPPluslusterFactory(AbstractClusterFactory):
    def create_cluster(self, server: str, cluster_data: ClusterData) -> AbstractCluster:
        return OCPPlusCluster(server, cluster_data)

    def create_cluster_using_cluster_name(self, cluster_name: str, cluster_data: ClusterData) -> AbstractCluster:
        return OCPPlusCluster(f"https://api.{cluster_name}.cp.fyre.ibm.com:6443", cluster_data)

    def get_cluster_type_name(self) -> str:
        return "FYRE (OCP+)"


ocpplus_cluster_factory = OCPPluslusterFactory()
