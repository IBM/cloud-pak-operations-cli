#  Copyright 2023 IBM Corporation
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

from functools import total_ordering


@total_ordering
class PackageDirectoryDetails:
    def __init__(self, distribution_package_name: str, package_directory_path: pathlib.Path):
        self._distribution_package_name = distribution_package_name
        self._package_directory_path = package_directory_path

    def __eq__(self, other: "PackageDirectoryDetails") -> bool:
        return (self.distribution_package_name == other.distribution_package_name) and (
            self.package_directory_path == other.package_directory_path
        )

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other: "PackageDirectoryDetails") -> bool:
        return (
            self.distribution_package_name < other.distribution_package_name
            if self.distribution_package_name != other.distribution_package_name
            else self.package_directory_path < other.package_directory_path
        )

    @property
    def distribution_package_name(self) -> str:
        return self._distribution_package_name

    @property
    def package_directory_path(self) -> pathlib.Path:
        return self._package_directory_path
