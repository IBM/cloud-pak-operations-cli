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
import pathlib

from importlib.metadata import entry_points
from types import ModuleType
from typing import Dict, Optional

from cpo.lib.error import DataGateCLIException
from cpo.lib.plugin_manager.distribution_entry_point_loader import (
    DistributionEntryPointLoader,
)
from cpo.lib.plugin_manager.package_data import PackageData

logger = logging.getLogger(__name__)


class PluginManager:
    """
    Imports and manages packages provided by CLI plug-ins (i.e., other
    distribution packages)

    To add Click commands or command groups to a built-in command group, CLI
    plug-ins (i.e., distribution packages) must export packages by
    specifying one or more entry points within the
    cloud_pak_operations_cli_plugins group in their configuration file.

    To specify the built-in command group, the __doc__ attribute of the
    __init__.py module of an entry point package must be set to the path of
    the built-in command group in the command hierarchy. Nested built-in
    command groups must be separated by slashes. If the __doc__ attribute is
    not set, Click commands or command groups are added to the root
    command group.

    Examples
    --------
    1. Package structure

    package_1
    | __init__.py (__doc__ = "")
    | … (modules and subpackages)
    package_2
    | __init__.py (__doc__ = "adm/config")
    | … (modules and subpackages)

    2. setup.cfg:

    [options.entry_points]
    cloud_pak_operations_cli_plugins =
        entry_point_1 = package_1
        entry_point_2 = package_2

    Notes
    -----
    https://packaging.python.org/guides/creating-and-discovering-plugins/#using-package-metadata
    """

    def __init__(self):
        self._package_data_dict: Optional[Dict[str, PackageData]] = None

    def reload(self):
        """Reloads CLI plug-ins"""

        self._package_data_dict = None

        self._load_plugins_if_required()

    @property
    def package_data_dict(self) -> Dict[str, PackageData]:
        self._load_plugins_if_required()

        assert self._package_data_dict is not None

        return self._package_data_dict

    def _load_plugins_if_required(self):
        """Loads CLI plug-ins if required"""

        if self._package_data_dict is not None:
            return

        self._package_data_dict = {}

        selected_entry_points = entry_points().get("cloud_pak_operations_cli_plugins")

        if selected_entry_points is None:
            return

        for entry_point in selected_entry_points:
            distribution_entry_point_loader = DistributionEntryPointLoader(entry_point)

            if distribution_entry_point_loader.distribution is None:
                raise DataGateCLIException(f"Distribution for entry point '{entry_point.name}' not found")

            distribution_package_name = distribution_entry_point_loader.distribution.metadata["name"]

            if not isinstance(distribution_entry_point_loader.loaded_entry_point, ModuleType):
                raise DataGateCLIException(
                    f"Entry point '{entry_point.name}' (distribution package: {distribution_package_name}) is not "
                    f"a package"
                )

            module: ModuleType = distribution_entry_point_loader.loaded_entry_point

            if module.__file__ is None or pathlib.Path(module.__file__).name != "__init__.py":
                raise DataGateCLIException(
                    f"Entry point '{entry_point.name}' (distribution package: {distribution_package_name}) is not "
                    f"a package"
                )

            command_hierarchy_path = module.__doc__ if module.__doc__ is not None else ""

            logger.debug(
                f"Importing package '{entry_point.value}' [distribution package: {distribution_package_name}, path: "
                f"{module.__file__}, command hierarchy path: '{command_hierarchy_path}']"
            )

            self._process_package(
                distribution_package_name, command_hierarchy_path, pathlib.Path(module.__file__).parent
            )

        for package_data in self._package_data_dict.values():
            package_data.modules.sort(
                key=lambda packge_element_data: (
                    packge_element_data.distribution_package_name,
                    packge_element_data.name,
                )
            )

            package_data.subpackages.sort(
                key=lambda packge_element_data: (
                    packge_element_data.distribution_package_name,
                    packge_element_data.name,
                )
            )

    def _process_package(
        self, distribution_package_name: str, command_hierarchy_path: str, package_directory_path: pathlib.Path
    ):
        assert self._package_data_dict is not None

        if command_hierarchy_path not in self._package_data_dict:
            self._package_data_dict[command_hierarchy_path] = PackageData()

        package_data = PackageData.get_package_data(
            distribution_package_name, command_hierarchy_path, package_directory_path
        )

        for module in package_data.modules:
            self._package_data_dict[command_hierarchy_path].modules.append(module)

        for subpackage in package_data.subpackages:
            self._package_data_dict[command_hierarchy_path].subpackages.append(subpackage)


plugin_manager = PluginManager()
