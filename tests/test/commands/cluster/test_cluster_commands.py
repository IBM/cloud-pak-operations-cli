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

import cpo.config
import cpo.lib.cluster
import cpo.lib.cluster.cluster_factory

from cpo.config.cluster_credentials_manager import cluster_credentials_manager
from cpo.cpo import cli
from cpo.lib.cluster.cluster import AbstractCluster, ClusterData


class UnitTestClusterData(TypedDict):
    alias: str
    server: str


class UnitTestCluster(AbstractCluster):
    def __init__(self, server: str, cluster_data: ClusterData):
        super().__init__(server, cluster_data)

    # override
    def get_password(self) -> str:
        return ""

    # override
    def get_username(self) -> str:
        return ""

    # override
    def login(self):
        pass


class UnitTestClusterFactory(cpo.lib.cluster.cluster_factory.AbstractClusterFactory):
    def create_cluster(self, server: str, cluster_data: ClusterData) -> AbstractCluster:
        return UnitTestCluster(server, cluster_data)

    def get_cluster_type_name(self):
        return ""


cpo.lib.cluster.cluster_factories["Unit Test"] = UnitTestClusterFactory()


class TestClusterCommands(unittest.TestCase):
    def setUp(self):
        clusters_file_path = pathlib.Path(tempfile.gettempdir()) / "clusters.json"

        if clusters_file_path.exists():
            os.remove(clusters_file_path)

        cluster_credentials_manager.get_clusters_file_path = unittest.mock.MagicMock(return_value=clusters_file_path)

        cluster_credentials_manager.reload()

    def test_current_and_use_commands(self):
        # create cluster-1 and check that current cluster is not set
        cluster_1_data = self._cluster_1_data()

        self._add_cluster(cluster_1_data)
        self.assertEqual(self._get_current_cluster(), "")

        # set cluster-1 as current cluster using alias and check that current
        # cluster is set to cluster-1
        self._use_cluster(cluster_1_data["alias"])
        self.assertEqual(self._get_current_cluster().rstrip(), cluster_1_data["server"])

        # create cluster-2 and check that current cluster is still set to
        # cluster-1
        cluster_2_data = self._cluster_2_data()

        self._add_cluster(cluster_2_data)
        self.assertEqual(self._get_current_cluster().rstrip(), cluster_1_data["server"])

        # set cluster-2 as current cluster using server URL and check that
        # current cluster is set to cluster-2
        self._use_cluster(cluster_2_data["server"])
        self.assertEqual(self._get_current_cluster().rstrip(), cluster_2_data["server"])

        # remove cluster-2 and check that current cluster is not set
        self._rm_cluster(cluster_2_data["server"])
        self.assertEqual(self._get_current_cluster().rstrip(), "")

    def test_edit_command(self):
        # create cluster-1 and cluster-2
        cluster_1_data = self._cluster_1_data()
        cluster_2_data = self._cluster_2_data()

        self._add_cluster(cluster_1_data)
        self._add_cluster(cluster_2_data)

        # edit alias and password for cluster-1
        self._edit_alias(cluster_1_data["server"], "cluster1-alias-changed")
        self._edit_password(cluster_1_data["server"], "password")

        cluster = cluster_credentials_manager.get_cluster(cluster_1_data["server"])

        self.assertIsNotNone(cluster)

        # prevent Pylance error ("get_cluster_data" is not a known member of "None")
        if cluster is None:
            raise TypeError()

        cluster_data = cluster.get_cluster_data()

        self.assertEqual(cluster_data["alias"], "cluster1-alias-changed")
        self.assertEqual(cluster_data["password"], "password")

        # set alias of cluster-2 to alias of cluster-1
        with self.assertRaisesRegex(Exception, "Alias already exists"):
            self._edit_alias(
                cluster_2_data["server"],
                "cluster1-alias-changed",
            )

    def test_rm_command(self):
        # create cluster-1
        cluster_1_data = self._cluster_1_data()
        cluster_2_data = self._cluster_2_data()

        self._add_cluster(cluster_1_data)
        self.assertEqual(
            len(cluster_credentials_manager.get_clusters_file_contents_with_default()["clusters"]),
            1,
        )

        # remove cluster-1
        self._rm_cluster(cluster_1_data["server"])
        self.assertEqual(
            len(cluster_credentials_manager.get_clusters_file_contents_with_default()["clusters"]),
            0,
        )

        # remove cluster-2
        server = cluster_2_data["server"]

        with self.assertRaisesRegex(Exception, f"Cluster not found \\({server}\\)"):
            self._rm_cluster(
                cluster_2_data["server"],
            )

    def _add_cluster(self, cluster_data: UnitTestClusterData):
        cluster_credentials_manager.add_cluster(
            cluster_data["alias"],
            cluster_data["server"],
            "Unit Test",
            {},
        )

    def _cluster_1_data(self) -> UnitTestClusterData:
        return {
            "alias": "cluster1-alias",
            "server": "cluster1.cloud.example.com:12345",
        }

    def _cluster_2_data(self) -> UnitTestClusterData:
        return {
            "alias": "cluster2-alias",
            "server": "cluster2.cloud.example.com:12345",
        }

    def _edit_alias(self, alias_or_server: str, alias: str):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            ["cluster", "edit", "--alias", alias, alias_or_server],
        )

        if result.exception is not None:
            raise (result.exception)

        self.assertEqual(result.exit_code, 0)

    def _edit_password(self, alias_or_server: str, password: str):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            ["cluster", "edit", "--password", password, alias_or_server],
        )

        self.assertEqual(result.exit_code, 0)

    def _get_current_cluster(self):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            [
                "cluster",
                "current",
            ],
        )

        self.assertEqual(result.exit_code, 0)

        return result.stdout

    def _rm_cluster(self, alias_or_server: str):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            ["cluster", "rm", alias_or_server],
        )

        if result.exception is not None:
            raise (result.exception)

        self.assertEqual(result.exit_code, 0)

    def _use_cluster(self, alias_or_server: str):
        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            ["cluster", "use", alias_or_server],
        )

        self.assertEqual(result.exit_code, 0)
