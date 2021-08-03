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

import importlib
import logging
import pathlib

from types import ModuleType
from typing import Dict, List, Optional, Type

import click

import dg.utils.debugger

logger = logging.getLogger(__name__)


class CommandData:
    def __init__(self, command_names: List[str], commands: Dict[str, click.Command]):
        super().__init__()

        self.command_names = command_names
        self.commands = commands


def create_click_multi_command_class(package: ModuleType) -> Type[click.Command]:
    """Creates a definition of a subclass of click.MultiCommand

    This method creates a definition of a subclass of click.MultiCommand
    providing Click commands found in the Python modules of the given Python
    package.

    Parameters
    ----------
    package
        Python package

    Returns
    -------
    click.Command
        Definition of a subclass of click.MultiCommand
    """

    package_name = package.__name__
    package_directory_path = pathlib.Path(package.__file__).parent

    class LazyLoadingMultiCommand(click.MultiCommand):
        def __call__(self, *args, **kwargs):
            """Handle exceptions raised by Click commands"""

            try:
                return self.main(*args, **kwargs)
            except Exception as exception:
                if dg.utils.debugger.is_debugpy_running():
                    # print stack trace
                    raise exception
                else:
                    click.ClickException(str(exception)).show()

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self._command_data: Optional[CommandData] = None

        def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
            self._initialize_commands_if_required()

            command: Optional[click.Command] = None

            if self._command_data is not None:
                command = self._command_data.commands[cmd_name] if cmd_name in self._command_data.commands else None

            return command

        def list_commands(self, ctx: click.Context) -> List[str]:
            self._initialize_commands_if_required()

            return self._command_data.command_names if self._command_data is not None else []

        def _get_click_commands(self, module: ModuleType) -> Dict[str, click.Command]:
            """Returns Click commands within the given Python module

            This method searches the given Python module for Click commands.

            Parameters
            ----------
            module
                Python module

            Returns
            -------
            dict[str, click.Command]
                dictionary associating Click command names with Click commands
            """

            commands: Dict[str, click.Command] = {}

            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)

                if isinstance(attribute, click.Command):
                    command_name = attribute_name.replace("_", "-")

                    commands[command_name] = attribute

            return commands

        def _import_packages_and_modules(self) -> Dict[str, ModuleType]:
            """Imports all subpackages and submodules within a Python package

            Parameters
            ----------
            package_name
                name of the Python package (__name__)
            package_directory_path
                path of the directory of the Python package (__file__)

            Returns
            -------
            dict[str, ModuleType]
                dictionary associating names of imported modules with imported modules
            """

            modules: Dict[str, ModuleType] = {}

            for file_path in package_directory_path.iterdir():
                if file_path.is_dir() and (file_path / "__init__.py").exists():
                    package_or_module_name = file_path.name

                    logger.debug(f"Importing package {package_name}.{package_or_module_name}")
                    modules[package_or_module_name] = importlib.import_module(
                        f"{package_name}.{package_or_module_name}"
                    )
                elif file_path.is_file() and (file_path.suffix == ".py") and (file_path.name != "__init__.py"):
                    package_or_module_name = file_path.name[:-3]

                    logger.debug(f"Importing module {package_name}.{package_or_module_name}")
                    modules[package_or_module_name] = importlib.import_module(
                        f"{package_name}.{package_or_module_name}"
                    )

            return modules

        def _initialize_commands_if_required(self):
            """Creates click.MultiCommand data structures

            This method creates two data structures based on Click commands within
            the given Python modules:

            - a list of Click command names
            - a dictionary associating Click command names with Click commands

            Parameters
            ----------
            modules
                Python modules
            """

            if self._command_data is None:
                commands: Dict[str, click.Command] = {}
                command_names: List[str] = []
                modules = self._import_packages_and_modules()

                for module_name, module in modules.items():
                    module_commands = self._get_click_commands(module)

                    if len(module_commands) != 0:
                        commands.update(module_commands)
                        command_names.append(module_name.replace("_", "-"))

                command_names.sort()

                self._command_data = CommandData(command_names, commands)

    return LazyLoadingMultiCommand
