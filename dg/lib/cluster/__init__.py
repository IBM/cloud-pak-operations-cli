from typing import Dict

import dg.lib.cluster.cluster_factory
import dg.lib.fyre.cluster
import dg.lib.fyre.cluster.ocpplus_cluster_factory
import dg.lib.ibmcloud.ks.cluster
import dg.lib.ibmcloud.ks.cluster.iks_cluster_factory
import dg.lib.ibmcloud.oc.cluster
import dg.lib.ibmcloud.oc.cluster.roks_cluster_factory

from dg.lib.cluster.cluster_factory import AbstractClusterFactory

cluster_factories: Dict[str, AbstractClusterFactory] = {}
cluster_factories[
    dg.lib.ibmcloud.ks.cluster.CLUSTER_TYPE_ID
] = dg.lib.ibmcloud.ks.cluster.iks_cluster_factory.iks_cluster_factory

cluster_factories[
    dg.lib.ibmcloud.oc.cluster.CLUSTER_TYPE_ID
] = dg.lib.ibmcloud.oc.cluster.roks_cluster_factory.roks_cluster_factory

cluster_factories[
    dg.lib.fyre.cluster.CLUSTER_TYPE_ID
] = dg.lib.fyre.cluster.ocpplus_cluster_factory.ocpplus_cluster_factory
