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

import os
import pathlib

from typing import Optional

import cpo.utils.process

from cpo.config.binaries_manager import binaries_manager
from cpo.lib.dependency_manager.dependency_manager_plugin import AbstractDependencyManagerPlugIn
from cpo.utils.error import CloudPakOperationsCLIException


class DependencyManager:
    """Responsible for managing dependencies"""

    def __init__(self):
        self._download_manager_dict: dict[type[AbstractDependencyManagerPlugIn], AbstractDependencyManagerPlugIn] = {}
        self._download_manager_plugins: list[AbstractDependencyManagerPlugIn] = []

    def execute_binary(
        self,
        cls: type[AbstractDependencyManagerPlugIn],
        args: list[str],
        env: dict[str, str] = os.environ.copy(),
        capture_output=False,
        check=True,
        print_captured_output=False,
    ) -> cpo.utils.process.ProcessResult:
        """Executes the binary provided by the dependency corresponding to the
        dependency manager plug-in of the given type

        If the dependency does not provide a binary with the given name, an
        exception is raised.

        Parameters
        ----------
        cls
            dependency manager plug-in type
        args
            arguments to be passed to the binary
        env
            dictionary of environment variables passed to the process
        capture_output
            flag indicating whether process output shall be captured
        check
            flag indicating whether an exception shall be thrown if the binary
            returns with a nonzero return code
        print_captured_output
            flag indicating whether captured process output shall also be written to
            stdout/stderr

        Returns
        -------
        ProcessResult
            object storing the return code and captured process output (if
            requested)
        """

        plugin = self._download_manager_dict.get(cls)

        if plugin is None:
            raise CloudPakOperationsCLIException(f"Plug-in with class name '{cls.__name__} was not registered")

        binary_path = plugin.get_binary_path()

        if binary_path is None:
            raise CloudPakOperationsCLIException(
                f"Dependency '{plugin.get_dependency_name()} does not provide a binary'"
            )

        if not binary_path.exists():
            latest_dependency_version = plugin.get_latest_dependency_version()

            plugin.download_dependency_version(latest_dependency_version)
            binaries_manager.set_binary_version(plugin.get_dependency_alias(), str(latest_dependency_version))

        return plugin.execute_binary(
            args, env, capture_output=capture_output, check=check, print_captured_output=print_captured_output
        )

    def get_binary_path(self, cls: type[AbstractDependencyManagerPlugIn]) -> Optional[pathlib.Path]:
        """Returns the path of the binary provided by the dependency
        corresponding to the dependency manager plug-in of the given type

        Returns
        -------
        cls
            dependency manager plug-in type
        Optional[pathlib.Path]
            path of the binary provided by the dependency corresponding to the
            dependency manager plug-in of the given type or None if the dependency
            does not provide a binary
        """

        plugin = self._download_manager_dict.get(cls)

        if plugin is None:
            raise CloudPakOperationsCLIException(f"Plug-in with class name '{cls.__name__} was not registered")

        return plugin.get_binary_path()

    def register_plugin(self, cls: type[AbstractDependencyManagerPlugIn]):
        """Registers a dependency manager plug-in of the given type

        Parameters
        ----------
        cls
            dependency manager plug-in type
        """

        plugin = cls()

        self._download_manager_dict[cls] = plugin
        self._download_manager_plugins.append(plugin)

    def download_dependencies_if_required(self):
        """Downloads dependencies if required

        The versions of the downloaded dependencies are stored in
        ~/.cpo/binaries.json.
        """

        for dependency_manager_plugin in self._download_manager_plugins:
            binary_alias = dependency_manager_plugin.get_dependency_alias()
            current_version = binaries_manager.get_binary_version(binary_alias)
            latest_dependency_version = dependency_manager_plugin.get_latest_dependency_version()

            if (current_version is None) or (latest_dependency_version.compare(current_version) == 1):
                dependency_manager_plugin.download_dependency_version(latest_dependency_version)
                binaries_manager.set_binary_version(binary_alias, str(latest_dependency_version))
