import dg.lib.cluster.cluster_factory
import dg.lib.fyre.cluster
import dg.lib.fyre.cluster.fyre_cluster_factory
import dg.lib.ibmcloud.oc.cluster
import dg.lib.ibmcloud.oc.cluster.roks_cluster_factory

from dg.lib.cluster.cluster_factory import AbstractClusterFactory

cluster_factories: dict[str, AbstractClusterFactory] = {}
cluster_factories[dg.lib.fyre.cluster.CLUSTER_TYPE_ID] = dg.lib.fyre.cluster.fyre_cluster_factory.fyre_cluster_factory
cluster_factories[
    dg.lib.ibmcloud.oc.cluster.CLUSTER_TYPE_ID
] = dg.lib.ibmcloud.oc.cluster.roks_cluster_factory.roks_cluster_factory
