from cpo.config.cluster_credentials_manager import cluster_credentials_manager


def get_current_cluster_alias():
    current_cluster = cluster_credentials_manager.get_current_cluster()

    if current_cluster is not None:
        cluster_data = current_cluster.get_cluster_data()

        if "alias" in cluster_data:
            print(cluster_data["alias"])
