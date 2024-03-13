#  Copyright 2021, 2024 IBM Corporation
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

from typing import Optional, TypeVar

import semver

import cpo.utils.operating_system
import cpo.utils.process

from cpo.config.binaries_manager import binaries_manager
from cpo.lib.dependency_manager.dependency_manager_binary_plugin import DependencyManagerBinaryPlugIn
from cpo.lib.dependency_manager.dependency_manager_plugin import AbstractDependencyManagerPlugIn, DependencyVersion
from cpo.lib.dependency_manager.plugins.ibm_cloud_cli_plugin import IBMCloudCLIPlugIn
from cpo.lib.dependency_manager.plugins.openshift.openshift_cli_plugin import OpenShiftCLIPlugIn
from cpo.lib.dependency_manager.plugins.openshift.openshift_install_plugin import OpenShiftInstallPlugIn
from cpo.utils.error import CloudPakOperationsCLIException

T = TypeVar("T", bound=AbstractDependencyManagerPlugIn)


class DependencyManager:
    """Responsible for managing dependencies"""

    @classmethod
    def get_instance(cls) -> "DependencyManager":
        """Returns the singleton instance of this class

        Returns
        -------
        DependencyManager
            singleton instance of this class
        """

        if DependencyManager._instance is None:
            DependencyManager._instance = DependencyManager()
            DependencyManager._instance.register_plugin(IBMCloudCLIPlugIn)
            DependencyManager._instance.register_plugin(OpenShiftCLIPlugIn)
            DependencyManager._instance.register_plugin(OpenShiftInstallPlugIn)

        return DependencyManager._instance

    def __init__(self):
        self._dependency_manager_dict: dict[type[AbstractDependencyManagerPlugIn], AbstractDependencyManagerPlugIn] = {}
        self._dependency_manager_plugins: list[AbstractDependencyManagerPlugIn] = []

    def download_dependency_if_required(self, cls: type[AbstractDependencyManagerPlugIn]) -> semver.Version:
        """Downloads a dependency if required

        Parameters
        ----------
        cls
            dependency manager plug-in type

        Returns
        -------
        semver.Version
            version of the downloaded dependency
        """

        plugin = self.get_plugin_for_plugin_class(cls)
        latest_downloaded_binary_version = binaries_manager.get_latest_downloaded_binary_version(
            plugin.get_dependency_alias()
        )

        if latest_downloaded_binary_version is None:
            latest_downloaded_binary_version = self._download_dependency(plugin)

        return latest_downloaded_binary_version.version

    def download_latest_dependencies_if_required(self):
        """Downloads latest dependencies if required

        The versions of the downloaded dependencies are stored in
        ~/.cpo/binaries.json.
        """

        for dependency_manager_plugin in self._dependency_manager_plugins:
            if dependency_manager_plugin.is_operating_system_supported(
                cpo.utils.operating_system.get_operating_system()
            ):
                binary_alias = dependency_manager_plugin.get_dependency_alias()
                latest_downloaded_binary_version = binaries_manager.get_latest_downloaded_binary_version(binary_alias)
                latest_dependency_version = dependency_manager_plugin.get_latest_dependency_version()

                if (latest_downloaded_binary_version is None) or (
                    latest_dependency_version.version.compare(latest_downloaded_binary_version.version) == 1
                ):
                    self._download_dependency(dependency_manager_plugin, latest_dependency_version)

    def execute_binary(
        self,
        cls: type[DependencyManagerBinaryPlugIn],
        version: semver.Version | str | None,
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
        version
            version of the dependency
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

        dependency_version: Optional[DependencyVersion] = None

        if isinstance(version, semver.Version):
            dependency_version = DependencyVersion(version)
        elif isinstance(version, str):
            dependency_version = AbstractDependencyManagerPlugIn.parse_as_semantic_version(version)

        plugin = self.get_plugin_for_plugin_class(cls)

        assert isinstance(plugin, DependencyManagerBinaryPlugIn)

        latest_downloaded_binary_version = binaries_manager.get_latest_downloaded_binary_version(
            plugin.get_dependency_alias()
        )

        if dependency_version is None:
            if latest_downloaded_binary_version is None:
                latest_dependency_version = plugin.get_latest_dependency_version()

                plugin.download_dependency_version(latest_dependency_version)
                binaries_manager.set_latest_downloaded_binary_version(
                    plugin.get_dependency_alias(), latest_dependency_version.version
                )

                latest_downloaded_binary_version = latest_dependency_version

            dependency_version = latest_downloaded_binary_version
        elif not plugin.get_binary_path(dependency_version.version).exists():
            plugin.download_dependency_version(dependency_version)

            if (latest_downloaded_binary_version is None) or (
                latest_downloaded_binary_version is not None
                and dependency_version.version > latest_downloaded_binary_version.version
            ):
                binaries_manager.set_latest_downloaded_binary_version(
                    plugin.get_dependency_alias(), dependency_version.version
                )

        return plugin.execute_binary(
            dependency_version.version,
            args,
            env,
            capture_output=capture_output,
            check=check,
            print_captured_output=print_captured_output,
        )

    def get_binary_path(self, cls: type[DependencyManagerBinaryPlugIn], version: semver.Version) -> pathlib.Path | None:
        """Returns the path of the binary provided by the dependency
        corresponding to the dependency manager plug-in of the given type

        Parameters
        ----------
        cls
            dependency manager plug-in type
        version
            version of the dependency

        Returns
        -------
        Optional[pathlib.Path]
            path of the binary provided by the dependency corresponding to the
            dependency manager plug-in of the given type or None if the dependency
            does not provide a binary
        """

        plugin = self.get_plugin_for_plugin_class(cls)

        assert isinstance(plugin, DependencyManagerBinaryPlugIn)

        return plugin.get_binary_path(version)

    def get_plugin_for_plugin_class(self, cls: type[T]) -> T:
        """Returns an instance of the given plug-in class

        Parameters
        ----------
        cls
            dependency manager plug-in type

        Returns
        -------
        T
            instance of the given plug-in class
        """

        plugin = self._dependency_manager_dict.get(cls)

        if plugin is None:
            raise CloudPakOperationsCLIException(f"Plug-in for class name '{cls.__name__}' is not registered")

        if not isinstance(plugin, cls):
            raise CloudPakOperationsCLIException(
                f"Plug-in for class name '{cls.__name__}' is not a subclass of this class"
            )

        return plugin

    def register_plugin(self, cls: type[AbstractDependencyManagerPlugIn]):
        """Registers a dependency manager plug-in of the given type

        Parameters
        ----------
        cls
            dependency manager plug-in type
        """

        plugin = cls()

        self._dependency_manager_dict[cls] = plugin
        self._dependency_manager_plugins.append(plugin)

    def _download_dependency(
        self, plugin: AbstractDependencyManagerPlugIn, dependency_version: DependencyVersion | None = None
    ) -> DependencyVersion:
        if dependency_version is None:
            dependency_version = plugin.get_latest_dependency_version()

        plugin.download_dependency_version(dependency_version)
        binaries_manager.set_latest_downloaded_binary_version(plugin.get_dependency_alias(), dependency_version.version)

        return dependency_version

    _instance: Optional["DependencyManager"] = None
