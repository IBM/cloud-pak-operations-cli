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

from dataclasses import dataclass
from typing import Optional


@dataclass
class PackageElementDescriptor:
    command_hierarchy_path: Optional[str]
    distribution_package_name: str
    name: str
    path: pathlib.Path


class PackageData:
    """Stores descriptors for modules and subpackages within a
    package"""

    @staticmethod
    def get_package_data(
        distribution_package_name: str, command_hierarchy_path: Optional[str], package_path: pathlib.Path
    ) -> "PackageData":
        """Creates an object describing modules and subpackages within the
        package with the given path

        Parameters
        ----------
        distribution_package_name
            name of the distribution package providing the package with the given
            path
        command_hierarchy_path
            path within the Click command hierarchy where Click commands or command
            groups shall be integrated
        package_path
            package path

        Returns
        -------
        PackageData
            object describing modules and subpackages within the package with the
            given path
        """

        package_data = PackageData()

        for file_path in package_path.iterdir():
            if file_path.is_dir() and (file_path / "__init__.py").exists():
                package_data.subpackages.append(
                    PackageElementDescriptor(
                        command_hierarchy_path, distribution_package_name, file_path.name, file_path / "__init__.py"
                    )
                )
            elif file_path.is_file() and (file_path.suffix == ".py"):
                package_data.modules.append(
                    PackageElementDescriptor(
                        command_hierarchy_path, distribution_package_name, file_path.name[:-3], file_path
                    )
                )

        return package_data

    def __init__(self):
        self._modules: list[PackageElementDescriptor] = []
        self._subpackages: list[PackageElementDescriptor] = []

    @property
    def modules(self) -> list[PackageElementDescriptor]:
        return self._modules

    @property
    def subpackages(self) -> list[PackageElementDescriptor]:
        return self._subpackages
