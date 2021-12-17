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

import cpo.utils.logging

from cpo.config import configuration_manager
from cpo.cpo import cli
from cpo.lib.error import DataGateCLIException

cpo.utils.logging.init_root_logger()


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
        cli_data_directory_path = pathlib.Path(tempfile.gettempdir()) / ".cpo"

        if cli_data_directory_path.exists():
            shutil.rmtree(cli_data_directory_path)

        configuration_manager.get_cli_data_directory_path = unittest.mock.MagicMock(
            return_value=cli_data_directory_path
        )

        TestFYRECommands._logger.setLevel("INFO")
        TestFYRECommands._log_in_to_fyre()

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

        # 1. Test cpo.commands.fyre.cluster package
        self._create_cluster()

        # 1.1 Test cpo.commands.fyre.cluster package (R/O)
        self._cluster_action_without_force(ClusterActionWithoutForce.DETAILS)
        self._cluster_action_without_force(ClusterActionWithoutForce.STATUS)

        # 1.2 Test cpo.commands.fyre.cluster package (R/W)
        self._cluster_action(ClusterAction.SHUTDOWN)
        self._cluster_action(ClusterAction.BOOT)
        self._cluster_action(ClusterAction.REBOOT)
        self._add_worker_node()
        self._node_action("worker3", NodeAction.SHUTDOWN_NODE)
        self._node_action("worker3", NodeAction.BOOT_NODE)
        self._node_action("worker3", NodeAction.REBOOT_NODE)

        result = self._node_action("worker3", NodeAction.REDEPLOY_NODE, ignore_exception=True)

        self._ignore_exception_if_regex_matches(
            result,
            "Failed to redeploy node \\(HTTP status code: 400\\) \\['No space available on any [p|x|z] host to "
            "redeploy vm for user id \\d+'\\]",
        )

        result = self._edit_inf_node(ignore_exception=True)

        self._ignore_exception_if_regex_matches(
            result,
            "Failed to .* \\(HTTP status code: 400\\) \\['product_group (disk|memory) quota exceeded for platform "
            "[p|x|z] for site (rtp|svl) for product group id \\d+'\\]",
        )

        self._edit_master_node("master0")

        result = self._edit_worker_node("worker3", ignore_exception=True)

        self._ignore_exception_if_regex_matches(
            result,
            "Failed to .* \\(HTTP status code: 400\\) \\['product_group (disk|memory) quota exceeded for platform "
            "[p|x|z] for site (rtp|svl) for product group id \\d+'\\]",
        )

        self._cluster_action_without_force(ClusterActionWithoutForce.DISABLE_DELETE)
        self._cluster_action_without_force(ClusterActionWithoutForce.ENABLE_DELETE)

        # 1.3 Test cpo.commands.fyre.info package
        self._check_hostname()
        self._get_default_size()
        self._invoke_cli_command(["fyre", "info", "get-openshift-versions-all-platforms"])
        self._invoke_cli_command(["fyre", "info", "get-quick-burn-max-hours"])
        self._invoke_cli_command(["fyre", "info", "get-quick-burn-sizes"])

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

        self._invoke_cli_command(args)

    def _check_hostname(self):
        assert TestFYRECommands._cluster_name is not None

        result = self._invoke_cli_command(
            ["fyre", "info", "check-cluster-name", "--cluster-name", TestFYRECommands._cluster_name]
        )

        self.assertRegex(
            result.output,
            f"Hostname {TestFYRECommands._cluster_name}\\.cp\\.fyre\\.ibm\\.com is not available \\(owning user: "
            f"\\d+\\)\\.",
        )

    def _cluster_action(self, cluster_action: ClusterAction):
        assert TestFYRECommands._cluster_name is not None

        self._invoke_cli_command(
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

        self._invoke_cli_command(
            [
                "fyre",
                "cluster",
                cluster_action.name.lower().replace("_", "-"),
                "--cluster-name",
                TestFYRECommands._cluster_name,
            ]
        )

    def _create_cluster(self):
        click_result = self._invoke_cli_command(["fyre", "cluster", "create"])
        search_result = regex.search("Created cluster '(.+)'", click_result.output)

        self.assertIsNotNone(search_result)

        if search_result is None:
            raise TypeError()

        TestFYRECommands._cluster_name = search_result.group(1)

    def _edit_inf_node(self, ignore_exception=False) -> click.testing.Result:
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

        return self._invoke_cli_command(args, ignore_exception)

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

        self._invoke_cli_command(args)

    def _edit_worker_node(self, node_name: str, ignore_exception=False) -> click.testing.Result:
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

        return self._invoke_cli_command(args, ignore_exception)

    def _get_default_size(self):
        self._invoke_cli_command(["fyre", "info", "get-default-sizes", "--platform", "p"])
        self._invoke_cli_command(["fyre", "info", "get-default-sizes", "--platform", "x"])
        self._invoke_cli_command(["fyre", "info", "get-default-sizes", "--platform", "z"])

    def _ignore_exception_if_regex_matches(self, result: click.testing.Result, pattern: str):
        if (
            result.exit_code != 0
            and result.exception is not None
            and isinstance(result.exception, DataGateCLIException)
        ):
            exception: DataGateCLIException = result.exception

            if regex.match(pattern, exception.get_error_message()) is None:
                self._check_result(result)
            else:
                TestFYRECommands._logger.info(f"Ignoring exception: {exception.get_error_message()}")

    def _install_db2_data_gate_stack(self):
        args = ["cluster", "install-db2-data-gate-stack", "--storage-vendor", "nfs"]

        self._invoke_cli_command(args)

    def _invoke_cli_command(self, args: List[str], ignore_exception=False) -> click.testing.Result:
        TestFYRECommands._logger.info(f"Testing: cpo {' '.join(args)}")

        runner = click.testing.CliRunner()
        result = runner.invoke(cli, args)

        if not ignore_exception:
            TestFYRECommands._check_result(result)

        return result

    def _node_action(self, node_name: str, cluster_action: NodeAction, ignore_exception=False) -> click.testing.Result:
        assert TestFYRECommands._cluster_name is not None

        return self._invoke_cli_command(
            [
                "fyre",
                "cluster",
                cluster_action.name.lower().replace("_", "-"),
                "--cluster-name",
                TestFYRECommands._cluster_name,
                "--force",
                "--node-name",
                node_name,
            ],
            ignore_exception=ignore_exception,
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
                "--fyre-api-user-name",
                fyre_api_user_name,
            ],
        )

        TestFYRECommands._check_result(result)

    _cluster_name: Optional[str] = None
    _logger = logging.getLogger(__name__)


if __name__ == "__main__":
    unittest.main()
