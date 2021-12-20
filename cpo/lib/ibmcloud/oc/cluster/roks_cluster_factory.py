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
from cpo.lib.ibmcloud.oc.cluster.roks_cluster import ROKSCluster


class ROKSClusterFactory(AbstractClusterFactory):
    def create_cluster(self, server: str, cluster_data: ClusterData) -> AbstractCluster:
        return ROKSCluster(server, cluster_data)

    def get_cluster_type_name(self) -> str:
        return "IBM Cloud (Red Hat OpenShift on IBM Cloud)"


roks_cluster_factory = ROKSClusterFactory()
