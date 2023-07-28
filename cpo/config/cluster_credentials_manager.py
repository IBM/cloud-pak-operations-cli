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

import json
import pathlib

from typing import Any, Optional, TypedDict

from tabulate import tabulate

import cpo.lib.cluster

from cpo.config import configuration_manager
from cpo.lib.cluster.cluster import AbstractCluster, ClusterData
from cpo.utils.error import CloudPakOperationsCLIException

ContextData = dict[str, Any]


class ClustersFileContents(TypedDict):
    clusters: dict[str, ClusterData]
    current_cluster: str


class ClusterCredentialsManager:
    """Manages registered OpenShift clusters"""

    def __init__(self):
        self._clusters_file_contents = self.get_clusters_file_contents_with_default()
        self._current_credentials: Optional[ContextData] = None

    def add_cluster(self, alias: str, server: str, type: str, cluster_data: ClusterData):
        """Registers an existing OpenShift cluster

        Parameters
        ----------
        alias
            alias used to reference the cluster instead of its server URL
        server
            Server URL of the OpenShift cluster
        cluster_data
            additional cluster data
        """

        if alias != "":
            self._raise_if_alias_or_server_exists(alias, server)

        cluster_data_copy = cluster_data.copy()
        cluster_data_copy["alias"] = alias
        cluster_data_copy["type"] = type

        clusters = self._get_clusters()
        clusters[server] = cluster_data_copy

        self._save_clusters_file()

    def edit_cluster(self, alias_or_server, cluster_data_to_be_added: ClusterData) -> AbstractCluster:
        """Edits metadata of a registered OpenShift cluster

        Parameters
        ----------
        alias_or_server
            alias or server URL of the registered OpenShift cluster to be edited
        cluster_data_to_be_added
            cluster data to be added to existing cluster data

        Returns
        -------
        AbstractCluster
            metadata of the registered OpenShift cluster with the given alias or
            server URL
        """

        cluster = self.get_cluster(alias_or_server)

        if cluster is None:
            raise CloudPakOperationsCLIException(f"Cluster not found ({alias_or_server})")

        if ("alias" in cluster_data_to_be_added) and ((new_alias := cluster_data_to_be_added["alias"]) != ""):
            self._raise_if_alias_exists(new_alias)

        cluster_data = cluster.get_cluster_data()

        for key, value in cluster_data_to_be_added.items():
            cluster_data[key] = value

        self._save_clusters_file()

        return cluster

    def get_cluster(self, alias_or_server) -> Optional[AbstractCluster]:
        """Returns metadata of the registered OpenShift cluster with the given
        alias or server URL

        Parameters
        ----------
        alias_or_server
            alias or server URL of the registered OpenShift cluster for which
            metadata shall be returned

        Returns
        -------
        Optional[AbstractCluster]
            metadata of the registered OpenShift cluster with the given alias or
            server URL or None if no cluster was found
        """

        result: Optional[AbstractCluster] = None

        for server, cluster_data in self._get_clusters().items():
            if (server == alias_or_server) or (
                ("alias" in cluster_data) and (cluster_data["alias"] == alias_or_server)
            ):
                cluster_factory = cpo.lib.cluster.cluster_factories[cluster_data["type"]]
                result = cluster_factory.create_cluster(server, cluster_data)

        return result

    def get_cluster_or_raise_exception(self, alias_or_server) -> AbstractCluster:
        """Returns metadata of the registered OpenShift cluster with the given
        alias or server URL

        Parameters
        ----------
        alias_or_server
            alias or server URL of the registered OpenShift cluster for which
            metadata shall be returned

        Returns
        -------
        AbstractCluster
            metadata of the registered OpenShift cluster with the given alias
        """

        cluster = self.get_cluster(alias_or_server)

        if cluster is None:
            raise CloudPakOperationsCLIException(f"Cluster not found ({alias_or_server})")

        return cluster

    def get_clusters_as_str(self) -> str:
        """Returns metadata of registered OpenShift clusters as a
        pretty-printed string

        Returns
        -------
        str
            metadata of registered OpenShift clusters as a pretty-printed string
        """

        cluster_list: list[list[str]] = []
        server_of_current_cluster = self._get_server_of_current_cluster()

        for server, cluster_data in self._get_clusters().items():
            alias = cluster_data["alias"] if "alias" in cluster_data else ""
            cluster_factory = cpo.lib.cluster.cluster_factories[cluster_data["type"]]

            cluster_list_element: list[str] = [
                "*" if (server == server_of_current_cluster) else "",
                server,
                alias,
                cluster_factory.get_cluster_type_name(),
            ]

            cluster_list.append(cluster_list_element)

        result = tabulate(cluster_list, headers=["", "server", "alias", "type"])

        return result

    def get_clusters_file_contents(self) -> Optional[ClustersFileContents]:
        """Returns the contents of the clusters file

        Returns
        -------
        Optional[ClustersFileContents]
            contents of the clusters file or None if it does not exist
        """

        clusters_file_contents: Optional[ClustersFileContents] = None
        clusters_file_path = self.get_clusters_file_path()

        if clusters_file_path.exists():
            with open(clusters_file_path) as clusters_file:
                clusters_file_contents = json.load(clusters_file)

        return clusters_file_contents

    def get_clusters_file_contents_with_default(self) -> ClustersFileContents:
        """Returns the contents of the clusters file or a default value

        Returns
        -------
        ClustersFileContents
            contents of the clusters file or a default value if it does not exist
        """

        clusters_file_contents: Optional[ClustersFileContents] = self.get_clusters_file_contents()

        if clusters_file_contents is None:
            clusters_file_contents = {"clusters": {}, "current_cluster": ""}

        return clusters_file_contents

    def get_clusters_file_path(self) -> pathlib.Path:
        """Returns the path of the clusters file

        Returns
        -------
        str
            path of the clusters file
        """

        return configuration_manager.get_cli_data_directory_path() / "clusters.json"

    def get_current_cluster(self) -> Optional[AbstractCluster]:
        """Returns metadata of the current registered OpenShift cluster

        Returns
        -------
        Optional[AbstractCluster]
            metadata of the current registered OpenShift cluster or None if no
            current cluster is set
        """

        cluster: Optional[AbstractCluster] = None
        server_of_current_cluster = self._get_server_of_current_cluster()

        if server_of_current_cluster != "":
            cluster = self.get_cluster(server_of_current_cluster)

            if cluster is None:
                raise CloudPakOperationsCLIException("Current cluster not found")

        return cluster

    def get_current_credentials(self) -> ContextData:
        """Returns user and current cluster credentials

        User credentials are obtained from ~/.cpo/credentials.json. Cluster
        credentials are obtained from ~/.cpo/clusters.json.

        Returns
        -------
        ContextData
            user and current cluster credentials
        """

        if self._current_credentials is None:
            credentials_file_path = configuration_manager.get_credentials_file_path()

            if credentials_file_path.exists() and (credentials_file_path.stat().st_size != 0):
                with open(credentials_file_path) as json_file:
                    self._current_credentials = json.load(json_file)
            else:
                self._current_credentials = {}

            current_cluster = self.get_current_cluster()

            if current_cluster is not None:
                self._current_credentials.update(current_cluster.get_cluster_data())
                self._current_credentials["server"] = current_cluster.get_server()

        return self._current_credentials

    def raise_if_alias_exists(self, alias_to_be_searched: str):
        """Raises an exception if the given alias is already associated with a
        registered OpenShift cluster

        Parameters
        ----------
        alias_to_be_searched
            alias to be searched
        """

        clusters = self._get_clusters()

        for server, cluster_data in clusters.items():
            if ("alias" in cluster_data) and (cluster_data["alias"] == alias_to_be_searched):
                raise CloudPakOperationsCLIException("Alias already exists")

    def reload(self):
        """Reloads the clusters file"""

        self._clusters_file_contents = self.get_clusters_file_contents_with_default()

    def remove_cluster(self, alias_or_server: str):
        """Removes the registered OpenShift cluster with the given alias or
        server URL

        Parameters
        ----------
        alias_or_server
            alias or server URL of the registered OpenShift cluster to be removed
        """

        cluster = self.get_cluster(alias_or_server)

        if cluster is None:
            raise CloudPakOperationsCLIException(f"Cluster not found ({alias_or_server})")

        clusters = self._get_clusters()
        clusters.pop(cluster.get_server())

        if self._get_server_of_current_cluster() == cluster.get_server():
            self._clusters_file_contents["current_cluster"] = ""

        self._save_clusters_file()

    def set_cluster(self, alias_or_server: str) -> AbstractCluster:
        """Sets the current registered OpenShift cluster

        Parameters
        ----------
        alias_or_server
            alias or server URL of the registered OpenShift cluster to be set as
            the current cluster

        Returns
        -------
        AbstractCluster
            metadata of the registered OpenShift cluster with the given alias or
            server URL
        """

        cluster = self.get_cluster(alias_or_server)

        if cluster is None:
            raise CloudPakOperationsCLIException(f"Cluster not found ({alias_or_server})")

        self._clusters_file_contents["current_cluster"] = cluster.get_server()
        self._save_clusters_file()

        return cluster

    def _get_clusters(self) -> dict[str, ClusterData]:
        """Returns registered OpenShift clusters

        Returns
        -------
        dict[str, ClusterData]
            registered OpenShift clusters
        """

        if "clusters" not in self._clusters_file_contents:
            raise CloudPakOperationsCLIException("Corrupt configuration file")

        return self._clusters_file_contents["clusters"]

    def _get_server_of_current_cluster(self) -> str:
        """Returns the server URL of the current registered OpenShift cluster

        Returns
        -------
        str
            server URL of the current registered OpenShift cluster
        """

        return self._clusters_file_contents["current_cluster"]

    def _invalidate_current_credentials(self):
        """Invalidates current credentials"""

        self._current_credentials = None

    def _raise_if_alias_exists(self, alias_to_be_searched: str):
        """Raises an exception if the given alias is already associated with a
        registered OpenShift cluster

        Parameters
        ----------
        alias_to_be_searched
            alias to be searched
        """

        clusters = self._get_clusters()

        for cluster_data in clusters.values():
            if ("alias" in cluster_data) and (cluster_data["alias"] == alias_to_be_searched):
                raise CloudPakOperationsCLIException("Alias already exists")

    def _raise_if_alias_or_server_exists(self, alias_to_be_searched: str, server_to_be_searched: str):
        """Raises an exception if the given alias or server URL is already
        associated with a registered OpenShift cluster

        Parameters
        ----------
        alias_to_be_searched
            alias to be searched
        server_to_be_searched
            Server URL to be searched
        """

        clusters = self._get_clusters()

        for server, cluster_data in clusters.items():
            if server == server_to_be_searched:
                raise CloudPakOperationsCLIException("Server already exists")
            elif ("alias" in cluster_data) and (cluster_data["alias"] == alias_to_be_searched):
                raise CloudPakOperationsCLIException("Alias already exists")

    def _save_clusters_file(self):
        """Stores registered OpenShift clusters in a configuration file"""

        configuration_manager.get_cli_data_directory_path().mkdir(exist_ok=True)

        with open(self.get_clusters_file_path(), "w") as clusters_file:
            json.dump(
                self._clusters_file_contents,
                clusters_file,
                indent="\t",
                sort_keys=True,
            )

        self._invalidate_current_credentials()


cluster_credentials_manager = ClusterCredentialsManager()
