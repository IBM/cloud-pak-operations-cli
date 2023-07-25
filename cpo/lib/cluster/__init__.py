#  Copyright 2021, 2023 IBM Corporation
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

import cpo.lib.cluster.cluster_factory
import cpo.lib.ibmcloud.oc.cluster
import cpo.lib.ibmcloud.oc.cluster.roks_cluster_factory
import cpo.lib.openshift.cluster
import cpo.lib.openshift.cluster.generic_cluster_factory

from cpo.lib.cluster.cluster_factory import AbstractClusterFactory

cluster_factories: dict[str, AbstractClusterFactory] = {}
cluster_factories[
    cpo.lib.ibmcloud.oc.cluster.CLUSTER_TYPE_ID
] = cpo.lib.ibmcloud.oc.cluster.roks_cluster_factory.roks_cluster_factory

cluster_factories[
    cpo.lib.openshift.cluster.CLUSTER_TYPE_ID
] = cpo.lib.openshift.cluster.generic_cluster_factory.generic_cluster_factory
