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

import pathlib
import unittest
import unittest.mock

from types import ModuleType
from unittest.mock import Mock, patch

import click

import cpo
import tests.test.lib.plugin_manager.builtin_commands
import tests.test.lib.plugin_manager.plugin_1.package_1
import tests.test.lib.plugin_manager.plugin_1.package_2
import tests.test.lib.plugin_manager.plugin_1.package_3
import tests.test.lib.plugin_manager.plugin_1.package_4
import tests.test.lib.plugin_manager.plugin_2.package_1
import tests.test.lib.plugin_manager.plugin_2.package_2
import tests.test.lib.plugin_manager.plugin_2.package_3
import tests.test.lib.plugin_manager.plugin_2.package_4

from cpo.lib.click.lazy_loading_multi_command import LazyLoadingMultiCommand
from cpo.lib.plugin_manager.plugin_manager import plugin_manager
from cpo.utils.error import CloudPakOperationsCLIException


def create_entry_point_mock_objects(entry_points: list[tuple[str, ModuleType]]) -> list[Mock]:
    mock_objects: list[Mock] = []

    for distribution_package_name, module in entry_points:
        dist_mock_object = Mock()
        dist_mock_object.name = distribution_package_name

        mock_object = Mock(dist=dist_mock_object)
        mock_object.load.return_value = module

        mock_objects.append(mock_object)

    selectable_groups_mock_object = Mock()
    selectable_groups_mock_object.select.return_value = mock_objects

    return selectable_groups_mock_object


class TestPluginManager(unittest.TestCase):
    @patch(
        "cpo.lib.click.lazy_loading_multi_command.commands_package_path",
        pathlib.Path(tests.test.lib.plugin_manager.builtin_commands.__file__).parent,
    )
    @patch(
        "cpo.lib.plugin_manager.plugin_manager.entry_points",
        return_value=create_entry_point_mock_objects(
            [
                ("plugin-1", tests.test.lib.plugin_manager.plugin_1.package_1),
                ("plugin-1", tests.test.lib.plugin_manager.plugin_1.package_2),
                ("plugin-1", tests.test.lib.plugin_manager.plugin_1.package_3),
                ("plugin-1", tests.test.lib.plugin_manager.plugin_1.package_4),
            ]
        ),
    )
    def test_single_plugin(self, test_mock1):
        """Tests that commands provided by plugin-1 are correctly integrated

        - Command 'command-1' [package_1] is added to the top-level command
          group
        - Command group 'group-1' [package_2] is added to the top-level command
          group
        - Command 'bi-group-1-command-1' [package_3] is added to the
          command group 'bi-group-1'
        - Command 'bi-group-2-command-1' [package_4] is added to the
          command group 'bi-group-2' [within the command group 'bi-group-1']
        """

        plugin_manager.reload()

        multi_command_1 = LazyLoadingMultiCommand(
            cpo.distribution_package_name, tests.test.lib.plugin_manager.builtin_commands
        )

        multi_command_1_commands = multi_command_1.list_commands(Mock())

        self.assertEqual(len(multi_command_1_commands), 5)
        self.assertEqual(multi_command_1_commands[0], "bi-command-1")
        self.assertEqual(multi_command_1_commands[1], "bi-group-1")
        self.assertEqual(multi_command_1_commands[2], "command-1")
        self.assertEqual(multi_command_1_commands[3], "command-in-init-file")
        self.assertEqual(multi_command_1_commands[4], "group-1")

        multi_command_2 = multi_command_1.get_command(Mock(), "bi-group-1")

        self._assert_multi_command(multi_command_2)
        assert isinstance(multi_command_2, click.MultiCommand)

        multi_command_2_commands = multi_command_2.list_commands(Mock())

        self.assertEqual(len(multi_command_2_commands), 3)
        self.assertEqual(multi_command_2_commands[0], "bi-group-1-bi-command-1")
        self.assertEqual(multi_command_2_commands[1], "bi-group-1-command-1")
        self.assertEqual(multi_command_2_commands[2], "bi-group-2")

        multi_command_3 = multi_command_2.get_command(Mock(), "bi-group-2")

        self._assert_multi_command(multi_command_3)
        assert isinstance(multi_command_3, click.MultiCommand)

        multi_command_3_commands = multi_command_3.list_commands(Mock())

        self.assertEqual(len(multi_command_3_commands), 2)
        self.assertEqual(multi_command_3_commands[0], "bi-group-2-bi-command-1")
        self.assertEqual(multi_command_3_commands[1], "bi-group-2-command-1")

    @patch(
        "cpo.lib.click.lazy_loading_multi_command.commands_package_path",
        pathlib.Path(tests.test.lib.plugin_manager.builtin_commands.__file__).parent,
    )
    @patch(
        "cpo.lib.plugin_manager.plugin_manager.entry_points",
        return_value=create_entry_point_mock_objects(
            [
                ("plugin-2", tests.test.lib.plugin_manager.plugin_2.package_1),
            ]
        ),
    )
    def test_single_plugin_duplicate_command_error(self, test_mock1):
        """Tests that loading a plug-in providing a command that would override
        a built-in command fails
        """

        plugin_manager.reload()

        multi_command_1 = LazyLoadingMultiCommand(
            cpo.distribution_package_name, tests.test.lib.plugin_manager.builtin_commands
        )

        with self.assertRaisesRegex(
            CloudPakOperationsCLIException,
            f"Command 'bi-command-1' \\(distribution package: 'plugin-2', command hierarchy path: ''\\) cannot be "
            f"registered as a command with the same name was already provided by distribution package "
            f"'{cpo.distribution_package_name}'",
        ):
            multi_command_1.list_commands(Mock())

    @patch(
        "cpo.lib.click.lazy_loading_multi_command.commands_package_path",
        pathlib.Path(tests.test.lib.plugin_manager.builtin_commands.__file__).parent,
    )
    @patch(
        "cpo.lib.plugin_manager.plugin_manager.entry_points",
        return_value=create_entry_point_mock_objects(
            [
                ("plugin-2", tests.test.lib.plugin_manager.plugin_2.package_2),
            ]
        ),
    )
    def test_single_plugin_duplicate_command_group_error(self, test_mock1):
        """Tests that loading a plug-in providing a command group whose name
        equals the name of a built-in command group adds the commands within the
        command group provided by the plug-in to the built-in command group
        """

        plugin_manager.reload()

        multi_command_1 = LazyLoadingMultiCommand(
            cpo.distribution_package_name, tests.test.lib.plugin_manager.builtin_commands
        )

        multi_command_2 = multi_command_1.get_command(Mock(), "bi-group-1")

        assert multi_command_2 is not None
        assert isinstance(multi_command_2, LazyLoadingMultiCommand)

        multi_command_2_commands = multi_command_2.list_commands(Mock())

        self.assertEqual(len(multi_command_2_commands), 3)
        self.assertEqual(multi_command_2_commands[0], "bi-group-1-bi-command-1")
        self.assertEqual(multi_command_2_commands[1], "bi-group-2")
        self.assertEqual(multi_command_2_commands[2], "command-1")

    @patch(
        "cpo.lib.click.lazy_loading_multi_command.commands_package_path",
        pathlib.Path(tests.test.lib.plugin_manager.builtin_commands.__file__).parent,
    )
    @patch(
        "cpo.lib.plugin_manager.plugin_manager.entry_points",
        return_value=create_entry_point_mock_objects(
            [
                ("plugin-1", tests.test.lib.plugin_manager.plugin_1.package_1),
                ("plugin-2", tests.test.lib.plugin_manager.plugin_2.package_3),
            ]
        ),
    )
    def test_multiple_plugins_duplicate_command_error(self, test_mock1):
        """Tests that loading multiple plug-ins providing the same command
        fails
        """

        plugin_manager.reload()

        multi_command_1 = LazyLoadingMultiCommand(
            cpo.distribution_package_name, tests.test.lib.plugin_manager.builtin_commands
        )

        with self.assertRaisesRegex(
            CloudPakOperationsCLIException,
            "Command 'command-1' \\(distribution package: 'plugin-2', command hierarchy path: ''\\) cannot be "
            "registered as a command with the same name was already provided by distribution package 'plugin-1'",
        ):
            multi_command_1.list_commands(Mock())

    @patch(
        "cpo.lib.click.lazy_loading_multi_command.commands_package_path",
        pathlib.Path(tests.test.lib.plugin_manager.builtin_commands.__file__).parent,
    )
    @patch(
        "cpo.lib.plugin_manager.plugin_manager.entry_points",
        return_value=create_entry_point_mock_objects(
            [
                ("plugin-1", tests.test.lib.plugin_manager.plugin_1.package_2),
                ("plugin-2", tests.test.lib.plugin_manager.plugin_2.package_4),
            ]
        ),
    )
    def test_multiple_plugins_duplicate_command_group_error(self, test_mock1):
        """Tests that loading multiple plug-ins providing the same command group
        succeeds"""

        plugin_manager.reload()

        multi_command_1 = LazyLoadingMultiCommand(
            cpo.distribution_package_name, tests.test.lib.plugin_manager.builtin_commands
        )

        multi_command_1_commands = multi_command_1.list_commands(Mock())

        self.assertEqual(len(multi_command_1_commands), 3)
        self.assertEqual(multi_command_1_commands[0], "bi-command-1")
        self.assertEqual(multi_command_1_commands[1], "bi-group-1")
        self.assertEqual(multi_command_1_commands[2], "group-1")

    def _assert_multi_command(self, command: click.Command | None):
        self.assertIsNotNone(command)
        assert command is not None
        self.assertIsInstance(command, click.MultiCommand)
