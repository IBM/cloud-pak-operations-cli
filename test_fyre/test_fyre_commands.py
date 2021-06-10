#  Copyright 2020 IBM Corporation
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

import logging
import os
import pathlib
import re as regex
import shutil
import tempfile
import unittest
import unittest.mock

from enum import Enum, auto
from typing import List, Optional

import click
import click.testing

import dg.utils.logging

from dg.config import data_gate_configuration_manager
from dg.dg import cli

dg.utils.logging.init_root_logger()


class ClusterAction(Enum):
    BOOT = auto()
    DETAILS = auto()
    REBOOT = auto()
    SHUTDOWN = auto()


class ClusterActionWithoutForce(Enum):
    DETAILS = auto()
    DISABLE_DELETE = auto()
    ENABLE_DELETE = auto()
    GET_CLUSTER_ACCESS_TOKEN = auto()
    INSTALL_NFS_STORAGE_CLASS = auto()
    STATUS = auto()


class NodeAction(Enum):
    BOOT_NODE = auto()
    REBOOT_NODE = auto()
    REDEPLOY_NODE = auto()
    SHUTDOWN_NODE = auto()


class NodeActionWithoutForce(Enum):
    INIT_NODE_FOR_DB2_DATA_GATE = auto()


class TestFYRECommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dg_directory_path = pathlib.Path(tempfile.gettempdir()) / ".dg"

        if dg_directory_path.exists():
            shutil.rmtree(dg_directory_path)

        data_gate_configuration_manager.get_dg_directory_path = unittest.mock.MagicMock(return_value=dg_directory_path)

        TestFYRECommands._logger.setLevel("INFO")
        TestFYRECommands._log_in_to_fyre()
        TestFYRECommands._store_github_api_key()

    @classmethod
    def tearDownClass(cls):
        if TestFYRECommands._cluster_name is not None:
            print()
            TestFYRECommands._logger.info(f"Deleting cluster '{TestFYRECommands._cluster_name}' …")

            runner = click.testing.CliRunner()
            result = runner.invoke(
                cli,
                [
                    "fyre",
                    "cluster",
                    "rm",
                    "--cluster-name",
                    TestFYRECommands._cluster_name,
                    "--force",
                ],
            )

            TestFYRECommands._check_result(result)

    def test_fyre_commands(self):
        """Tests FYRE commands"""

        # 1. Test dg.commands.fyre.cluster package
        self._create_cluster()

        # 1.1 Test dg.commands.fyre.cluster package (R/O)
        self._cluster_action_without_force(ClusterActionWithoutForce.DETAILS)
        # self._cluster_action_without_force(ClusterActionWithoutForce.GET_CLUSTER_ACCESS_TOKEN)
        self._cluster_action_without_force(ClusterActionWithoutForce.STATUS)

        # 1.2 Test dg.commands.fyre.cluster package (R/W)
        self._cluster_action(ClusterAction.SHUTDOWN)
        self._cluster_action(ClusterAction.BOOT)
        self._cluster_action(ClusterAction.REBOOT)
        self._add_worker_node()
        self._node_action("worker3", NodeAction.SHUTDOWN_NODE)
        self._node_action("worker3", NodeAction.BOOT_NODE)
        self._node_action("worker3", NodeAction.REBOOT_NODE)
        self._node_action("worker3", NodeAction.REDEPLOY_NODE)
        self._edit_inf_node()
        self._edit_master_node("master0")
        self._edit_worker_node("worker3")
        self._cluster_action_without_force(ClusterActionWithoutForce.DISABLE_DELETE)
        self._cluster_action_without_force(ClusterActionWithoutForce.ENABLE_DELETE)

        # 1.3 Install Db2 for z/OS Data Gate stack
        # self._cluster_action_without_force(ClusterActionWithoutForce.INSTALL_NFS_STORAGE_CLASS)
        # self._install_db2_data_gate_stack()

        # 2. Test dg.commands.fyre.info package
        self._check_hostname()
        self._get_default_size()
        self._invoke_dg_command(["fyre", "info", "get-openshift-versions-all-platforms"])
        self._invoke_dg_command(["fyre", "info", "get-quick-burn-max-hours"])
        self._invoke_dg_command(["fyre", "info", "get-quick-burn-sizes"])

    def _add_worker_node(self):
        args = [
            "fyre",
            "cluster",
            "add-worker-node",
            "--cluster-name",
            TestFYRECommands._cluster_name,
            "--force",
            "--worker-node-additional-disk-size",
            "200",
            "--worker-node-additional-disk-size",
            "200",
            "--worker-node-additional-disk-size",
            "200",
            "--worker-node-count",
            "1",
            "--worker-node-num-cpus",
            "8",
            "--worker-node-ram-size",
            "16",
        ]

        self._invoke_dg_command(args)

    def _check_hostname(self):
        assert TestFYRECommands._cluster_name is not None

        result = self._invoke_dg_command(
            ["fyre", "info", "check-cluster-name", "--cluster-name", TestFYRECommands._cluster_name]
        )

        self.assertRegex(
            result.output,
            f"Hostname {TestFYRECommands._cluster_name}\\.cp\\.fyre\\.ibm\\.com is not available \\(owning user: "
            f"\\d+\\)\\.",
        )

    def _cluster_action(self, cluster_action: ClusterAction):
        assert TestFYRECommands._cluster_name is not None

        self._invoke_dg_command(
            [
                "fyre",
                "cluster",
                cluster_action.name.lower().replace("_", "-"),
                "--cluster-name",
                TestFYRECommands._cluster_name,
                "--force",
            ]
        )

    def _cluster_action_without_force(self, cluster_action: ClusterActionWithoutForce):
        assert TestFYRECommands._cluster_name is not None

        self._invoke_dg_command(
            [
                "fyre",
                "cluster",
                cluster_action.name.lower().replace("_", "-"),
                "--cluster-name",
                TestFYRECommands._cluster_name,
            ]
        )

    def _create_cluster(self):
        click_result = self._invoke_dg_command(["fyre", "cluster", "create"])
        search_result = regex.search("Created cluster '(.+)'", click_result.output)

        self.assertIsNotNone(search_result)

        TestFYRECommands._cluster_name = search_result.group(1)

    def _edit_inf_node(self):
        args = [
            "fyre",
            "cluster",
            "edit-inf-node",
            "--additional-disk-size",
            "200",
            "--additional-disk-size",
            "200",
            "--cluster-name",
            TestFYRECommands._cluster_name,
            "--force",
        ]

        self._invoke_dg_command(args)

    def _edit_master_node(self, node_name: str):
        args = [
            "fyre",
            "cluster",
            "edit-master-node",
            "--cluster-name",
            TestFYRECommands._cluster_name,
            "--force",
            "--node-name",
            node_name,
            "--node-num-cpus",
            "8",
            "--node-ram-size",
            "64",
        ]

        self._invoke_dg_command(args)

    def _edit_worker_node(self, node_name: str):
        args = [
            "fyre",
            "cluster",
            "edit-worker-node",
            "--additional-disk-size",
            "200",
            "--additional-disk-size",
            "200",
            "--additional-disk-size",
            "200",
            "--cluster-name",
            TestFYRECommands._cluster_name,
            "--force",
            "--node-name",
            node_name,
            "--node-num-cpus",
            "16",
            "--node-ram-size",
            "64",
        ]

        self._invoke_dg_command(args)

    def _get_default_size(self):
        self._invoke_dg_command(["fyre", "info", "get-default-sizes", "--platform", "p"])
        self._invoke_dg_command(["fyre", "info", "get-default-sizes", "--platform", "x"])
        self._invoke_dg_command(["fyre", "info", "get-default-sizes", "--platform", "z"])

    def _install_db2_data_gate_stack(self):
        args = ["cluster", "install-db2-data-gate-stack", "--storage-class", "nfs-client"]

        self._invoke_dg_command(args)

    def _invoke_dg_command(self, args: List[str], expected_exit_code=0) -> click.testing.Result:
        TestFYRECommands._logger.info(f"Testing: dg {' '.join(args)}")

        runner = click.testing.CliRunner()
        result = runner.invoke(cli, args)

        TestFYRECommands._check_result(result)

        return result

    def _node_action(self, node_name: str, cluster_action: NodeAction):
        assert TestFYRECommands._cluster_name is not None

        self._invoke_dg_command(
            [
                "fyre",
                "cluster",
                cluster_action.name.lower().replace("_", "-"),
                "--cluster-name",
                TestFYRECommands._cluster_name,
                "--force",
                "--node-name",
                node_name,
            ]
        )

    @classmethod
    def _check_result(cls, result: click.testing.Result):
        if result.exception is not None:
            if isinstance(result.exception, SystemExit):
                click.echo(result.output)
            else:
                click.ClickException(str(result.exception)).show()

        assert result.exit_code == 0

    @classmethod
    def _log_in_to_fyre(cls):
        fyre_api_key = os.getenv("FYRE_API_KEY")
        fyre_api_user_name = os.getenv("FYRE_API_USER_NAME")

        assert fyre_api_key is not None
        assert fyre_api_user_name is not None

        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            [
                "fyre",
                "login",
                "--fyre-api-key",
                fyre_api_key,
                "--fyre-user-name",
                fyre_api_user_name,
            ],
        )

        TestFYRECommands._check_result(result)

    @classmethod
    def _store_github_api_key(cls):
        github_api_key = os.getenv("GITHUB_API_KEY")

        assert github_api_key is not None

        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            [
                "adm",
                "store-credentials",
                "--ibm-github-api-key",
                github_api_key,
            ],
        )

        TestFYRECommands._check_result(result)

    _cluster_name: Optional[str] = None
    _logger = logging.getLogger(__name__)


if __name__ == "__main__":
    unittest.main()