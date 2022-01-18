#  Copyright 2021, 2022 IBM Corporation
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

from typing import Dict

import cpo.lib.cluster.cluster_factory
import cpo.lib.fyre.cluster
import cpo.lib.fyre.cluster.ocpplus_cluster_factory
import cpo.lib.ibmcloud.ks.cluster
import cpo.lib.ibmcloud.ks.cluster.iks_cluster_factory
import cpo.lib.ibmcloud.oc.cluster
import cpo.lib.ibmcloud.oc.cluster.roks_cluster_factory

from cpo.lib.cluster.cluster_factory import AbstractClusterFactory

cluster_factories: Dict[str, AbstractClusterFactory] = {}
cluster_factories[
    cpo.lib.ibmcloud.ks.cluster.CLUSTER_TYPE_ID
] = cpo.lib.ibmcloud.ks.cluster.iks_cluster_factory.iks_cluster_factory

cluster_factories[
    cpo.lib.ibmcloud.oc.cluster.CLUSTER_TYPE_ID
] = cpo.lib.ibmcloud.oc.cluster.roks_cluster_factory.roks_cluster_factory

cluster_factories[
    cpo.lib.fyre.cluster.CLUSTER_TYPE_ID
] = cpo.lib.fyre.cluster.ocpplus_cluster_factory.ocpplus_cluster_factory
