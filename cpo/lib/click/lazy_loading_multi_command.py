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

import importlib
import importlib.metadata
import importlib.util
import logging
import pathlib

from dataclasses import dataclass, field
from types import ModuleType
from typing import Optional, cast

import click

from sortedcontainers import SortedSet

import cpo
import cpo.utils.debugger

from cpo import commands_package_path
from cpo.lib.click.package_directory_details import PackageDirectoryDetails
from cpo.lib.plugin_manager.package_data import PackageData, PackageElementDescriptor
from cpo.lib.plugin_manager.plugin_manager import plugin_manager
from cpo.utils.error import CloudPakOperationsCLIException

logger = logging.getLogger(__name__)


@dataclass
class CommandDetails:
    command: click.Command
    distribution_package_name: str


@dataclass
class CommandData:
    command_names: SortedSet = field(default_factory=SortedSet)
    commands: dict[str, CommandDetails] = field(default_factory=dict)


class LazyLoadingMultiCommand(click.Group):
    """Provides Click commands found within modules of the package passed to
    the constructor

    For each found subpackage of the package passed to the constructor, a
    Click command group is created.
    """

    def __call__(self, *args, **kwargs):
        """Handle exceptions raised by Click commands"""

        try:
            return self.main(*args, **kwargs)
        except Exception as exception:
            if cpo.utils.debugger.is_debugpy_running():
                # print stack trace
                raise exception
            else:
                error_message = str(exception)

                click.ClickException(error_message[7:] if error_message.startswith("Error: ") else error_message).show()

                return 1

    def __init__(self, distribution_package_name: str, package: ModuleType, **kwargs):
        super().__init__(**kwargs)

        assert package.__file__ is not None

        self._command_data: Optional[CommandData] = None
        self._package_directories = SortedSet(
            [PackageDirectoryDetails(distribution_package_name, pathlib.Path(package.__file__).parent)]
        )

    def add_package_directory_path(self, distribution_package_name: str, package: ModuleType):
        assert package.__file__ is not None

        self._package_directories.add(
            PackageDirectoryDetails(distribution_package_name, pathlib.Path(package.__file__).parent)
        )

    # override
    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        self._initialize_command_data_if_required()

        command: Optional[click.Command] = None

        if self._command_data is not None:
            command = self._command_data.commands[cmd_name].command if cmd_name in self._command_data.commands else None

        return command

    # override
    def list_commands(self, ctx: click.Context) -> list[str]:
        self._initialize_command_data_if_required()

        return self._command_data.command_names if self._command_data is not None else []

    def _append_distribution_package_name_to_help_text(
        self, help_text: Optional[str], distribution_package_name: str
    ) -> Optional[str]:
        suffix = f"[{distribution_package_name}]"

        return suffix if (help_text is None) or (help_text == "") else f"{help_text} {suffix}"

    def _import_module_from_file_location(self, package_element_descriptor: PackageElementDescriptor) -> ModuleType:
        """Imports the module corresponding to the given package element
        descriptor from a file location

        Parameters
        ----------
        package_element_descriptor
            object describing a module or a subpackage within a package

        Returns
        -------
        ModuleType
            imported module
        """

        spec = importlib.util.spec_from_file_location(package_element_descriptor.name, package_element_descriptor.path)

        assert spec is not None
        assert spec.loader is not None

        module = importlib.util.module_from_spec(spec)

        spec.loader.exec_module(module)

        return module

    def _import_modules(self, command_data: CommandData, modules: list[PackageElementDescriptor]):
        """Imports the given modules and updates the given command data object

        Parameters
        ----------
        command_data
            object storing Click command names and Click commands
        modules
            modules to be imported
        """

        for package_element_descriptor in modules:
            logger.debug(f"Importing module {package_element_descriptor.name}")

            module = self._import_module_from_file_location(package_element_descriptor)
            command_dict = self._search_for_commands(package_element_descriptor, module)

            if len(command_dict) == 0:
                continue

            for command_name in command_dict:
                if command_name in command_data.command_names:
                    self._raise_registration_error(command_name, command_data, package_element_descriptor)

                command_data.command_names.add(command_name)

            command_data.commands.update(command_dict)

    def _import_subpackages(self, command_data: CommandData, subpackages: list[PackageElementDescriptor]):
        """Imports the given subpackages and updates the given command data
        object

        Parameters
        ----------
        command_data
            object storing Click command names and Click commands
        subpackages
            subpackages to be imported
        """

        for package_element_descriptor in subpackages:
            logger.debug(f"Importing package {package_element_descriptor.name}")

            command_name = package_element_descriptor.name.replace("_", "-")

            if command_name in command_data.command_names:
                command_details = command_data.commands[command_name]

                if not isinstance(command_details.command, LazyLoadingMultiCommand):
                    self._raise_registration_error(command_name, command_data, package_element_descriptor)

                command_group = cast(LazyLoadingMultiCommand, command_details.command)
                command_group.add_package_directory_path(
                    package_element_descriptor.distribution_package_name,
                    self._import_module_from_file_location(package_element_descriptor),
                )
            else:
                package = self._import_module_from_file_location(package_element_descriptor)

                command_data.command_names.add(command_name)
                command_data.commands.update(
                    {
                        command_name: CommandDetails(
                            LazyLoadingMultiCommand(
                                package_element_descriptor.distribution_package_name,
                                package,
                                help=package.__doc__
                                if package_element_descriptor.distribution_package_name == cpo.distribution_package_name
                                else self._append_distribution_package_name_to_help_text(
                                    package.__doc__, package_element_descriptor.distribution_package_name
                                ),
                                name=None,
                            ),
                            package_element_descriptor.distribution_package_name,
                        )
                    }
                )

    def _initialize_command_data_if_required(self):
        """Creates a data structure based on modules and subpackges of the
        package passed to the constructor

        This data structure is used when Click calls the overriden methods
        get_command() and list_commands().
        """

        if self._command_data is not None:
            return

        command_data = CommandData()

        for element in self._package_directories:
            package_directory_details = cast(PackageDirectoryDetails, element)
            package_data = PackageData.get_package_data(
                package_directory_details.distribution_package_name,
                None,
                package_directory_details.package_directory_path,
            )

            self._import_modules(command_data, package_data.modules)
            self._import_subpackages(command_data, package_data.subpackages)

            if self._is_builtin_package(package_directory_details.package_directory_path):
                # LazyLoadingMultiCommand instance corresponds to a built-in package
                # (i.e., not a package provided by a plug-in)
                relative_path_to_commands_package = package_directory_details.package_directory_path.relative_to(
                    commands_package_path
                )

                command_hierarchy_path = (
                    str(relative_path_to_commands_package) if str(relative_path_to_commands_package) != "." else ""
                )

                if command_hierarchy_path in plugin_manager.package_data_dict:
                    plugin_package_data = plugin_manager.package_data_dict[command_hierarchy_path]

                    self._import_modules(command_data, plugin_package_data.modules)
                    self._import_subpackages(command_data, plugin_package_data.subpackages)

        self._command_data = command_data

    def _is_builtin_package(self, package_directory_path: pathlib.Path) -> bool:
        return package_directory_path.is_relative_to(commands_package_path)

    def _raise_registration_error(
        self, command_name: str, command_data: CommandData, package_element_descriptor: PackageElementDescriptor
    ):
        """Raises an error indicating that the Click command (group) with the
        given name already exists

        Parameters
        ----------
        command_name
            name of the Click command (group) that already exists
        command_data
            object storing Click command names and Click commands
        package_element_descriptor
            object describing a module or a subpackage within a package whereas the
            module or subpackage corresponds to the Click command (group) with the
            given name
        """

        command_type_1 = "Command group" if str(package_element_descriptor.path).endswith("__init__.py") else "Command"
        command_type_2 = (
            "command group"
            if isinstance(command_data.commands[command_name].command, click.MultiCommand)
            else "command"
        )

        command_hierarchy_path = (
            f", command hierarchy path: '{package_element_descriptor.command_hierarchy_path}'"
            if package_element_descriptor.command_hierarchy_path is not None
            else ""
        )

        raise CloudPakOperationsCLIException(
            f"{command_type_1} '{command_name}' (distribution package: '"
            f"{package_element_descriptor.distribution_package_name}'{command_hierarchy_path}) cannot be registered as "
            f"a {command_type_2} with the same name was already provided by distribution package '"
            f"{command_data.commands[command_name].distribution_package_name}'"
        )

    def _search_for_commands(
        self, package_element_descriptor: PackageElementDescriptor, module: ModuleType
    ) -> dict[str, CommandDetails]:
        """Searches the given module for Click commands

        Parameters
        ----------
        package_element_descriptor
            object describing a module or a subpackage within a package
        module
            module to be searched for Click commands

        Returns
        -------
        dict[str, click.Command]
            dictionary associating Click command names with Click commands
        """

        commands: dict[str, CommandDetails] = {}

        for attribute_name in dir(module):
            attribute = getattr(module, attribute_name)

            if isinstance(attribute, click.Command):
                if package_element_descriptor.distribution_package_name != cpo.distribution_package_name:
                    attribute.help = self._append_distribution_package_name_to_help_text(
                        attribute.help, package_element_descriptor.distribution_package_name
                    )

                command_name = attribute_name.replace("_", "-")

                commands[command_name] = CommandDetails(attribute, package_element_descriptor.distribution_package_name)

        return commands
