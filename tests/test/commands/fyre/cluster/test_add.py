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

import os
import pathlib
import tempfile
import unittest
import unittest.mock

from typing import TypedDict

import click.testing

import cpo.lib.fyre.cluster

from cpo.config.cluster_credentials_manager import cluster_credentials_manager
from cpo.cpo import cli
from cpo.lib.cluster.cluster import AbstractCluster


class ClusterData(TypedDict):
    alias: str
    cluster_name: str
    password: str
    server: str


class TestAddClusterCommands(unittest.TestCase):
    def test_add_cluster_command(self):
        clusters_file_path = pathlib.Path(tempfile.gettempdir()) / "clusters.json"

        if clusters_file_path.exists():
            os.remove(clusters_file_path)

        cluster_credentials_manager.get_clusters_file_path = unittest.mock.MagicMock(return_value=clusters_file_path)

        cluster_credentials_manager.reload()

        # create cluster-1 and check that the number of clusters is 1
        self._add_cluster_1()
        # create cluster-2 and check that the number of clusters is 2
        self._add_cluster_2()

        # create cluster-1 and check that the exit code of the command is 1 as
        # the server already exists
        with self.assertRaisesRegex(Exception, "Server already exists"):
            self._add_cluster_1()

        # create cluster-3 and check that the exit code of the command is 1 as
        # the alias already exists
        with self.assertRaisesRegex(Exception, "Alias already exists"):
            self._add_cluster_3()

    def _add_cluster(self, cluster_data: ClusterData, num_expected_cluster: int):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            [
                "fyre",
                "cluster",
                "add",
                "--alias",
                cluster_data["alias"],
                "--cluster-name",
                cluster_data["cluster_name"],
                "--password",
                cluster_data["password"],
            ],
        )

        if result.exception is not None:
            raise (result.exception)

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            len(cluster_credentials_manager.get_clusters_file_contents_with_default()["clusters"]),
            num_expected_cluster,
        )

        cluster = cluster_credentials_manager.get_cluster(cluster_data["server"])

        self.assertIsNotNone(cluster)

        if cluster is not None:
            self._check_cluster(cluster, cluster_data)

    def _add_cluster_1(self) -> ClusterData:
        cluster_1_data: ClusterData = {
            "alias": "cluster-1-alias",
            "cluster_name": "cluster-1",
            "password": "password",
            "server": "https://api.cluster-1.cp.fyre.ibm.com:6443",
        }

        self._add_cluster(cluster_1_data, 1)

        return cluster_1_data

    def _add_cluster_2(self) -> ClusterData:
        cluster_2_data: ClusterData = {
            "alias": "",
            "cluster_name": "cluster-2",
            "password": "password",
            "server": "https://api.cluster-2.cp.fyre.ibm.com:6443",
        }

        self._add_cluster(cluster_2_data, 2)

        return cluster_2_data

    def _add_cluster_3(self) -> ClusterData:
        cluster_3_data: ClusterData = {
            "alias": "cluster-1-alias",
            "cluster_name": "cluster-3",
            "password": "password",
            "server": "https://api.cluster-3.cp.fyre.ibm.com:6443",
        }

        self._add_cluster(cluster_3_data, 1)

        return cluster_3_data

    def _check_cluster(self, cluster: AbstractCluster, cluster_data: ClusterData):
        cluster_name = cluster_data["cluster_name"]
        returned_cluster_data = cluster.get_cluster_data()

        self.assertEqual(returned_cluster_data["alias"], cluster_data["alias"])
        self.assertEqual(returned_cluster_data["cluster_name"], cluster_name)
        self.assertEqual(
            returned_cluster_data["infrastructure_node_hostname"],
            f"api.{cluster_name}.cp.fyre.ibm.com",
        )

        self.assertEqual(returned_cluster_data["password"], cluster_data["password"])
        self.assertEqual(returned_cluster_data["type"], cpo.lib.fyre.cluster.CLUSTER_TYPE_ID)
        self.assertEqual(returned_cluster_data["username"], "kubeadmin")
