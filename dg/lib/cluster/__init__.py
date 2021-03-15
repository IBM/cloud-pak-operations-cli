import dg.lib.cluster.cluster_factory
import dg.lib.fyre.cluster
import dg.lib.fyre.cluster.fyre_cluster_factory
import dg.lib.ibmcloud.cluster
import dg.lib.ibmcloud.cluster.ibmcloud_cluster_factory

from dg.lib.cluster.cluster_factory import AbstractClusterFactory

cluster_factories: dict[str, AbstractClusterFactory] = {}
cluster_factories[dg.lib.fyre.cluster.CLUSTER_TYPE] = dg.lib.fyre.cluster.fyre_cluster_factory.fyre_cluster_factory
cluster_factories[
    dg.lib.ibmcloud.cluster.CLUSTER_TYPE
] = dg.lib.ibmcloud.cluster.ibmcloud_cluster_factory.ibm_cloud_cluster_factory
