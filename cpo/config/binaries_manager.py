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

import json
import pathlib

from typing import Optional

from cpo.config import configuration_manager

BinariesFileContents = dict[str, str]


class BinariesManager:
    """Manages downloaded binaries"""

    def __init__(self):
        self._binaries_file_contents: Optional[dict[str, str]] = None

    def get_binaries_file_contents(self) -> Optional[BinariesFileContents]:
        """Returns the contents of the binaries file

        Returns
        -------
        Optional[BinariesFileContents]
            contents of the binaries file or None if it does not exist
        """

        binaries_file_contents: Optional[BinariesFileContents] = None
        binaries_file_path = self.get_binaries_file_path()

        if binaries_file_path.exists():
            with open(binaries_file_path) as binaries_file:
                binaries_file_contents = json.load(binaries_file)

        return binaries_file_contents

    def get_binaries_file_contents_with_default(self) -> BinariesFileContents:
        """Returns the contents of the binaries file or a default value

        Returns
        -------
        BinariesFileContents
            contents of the binaries file or a default value if it does not exist
        """

        binaries_file_contents: Optional[BinariesFileContents] = self.get_binaries_file_contents()

        if binaries_file_contents is None:
            binaries_file_contents = {}

        return binaries_file_contents

    def get_binaries_file_path(self) -> pathlib.Path:
        """Returns the path of the binaries file

        Returns
        -------
        str
            path of the binaries file
        """

        return configuration_manager.get_cli_data_directory_path() / "binaries.json"

    def get_binary_version(self, binary_alias: str) -> Optional[str]:
        binaries = self._get_binary_versions()

        return binaries[binary_alias] if binary_alias in binaries else None

    def set_binary_version(self, binary_alias: str, version: str):
        binary_versions = self._get_binary_versions()

        binary_versions[binary_alias] = version
        self._save_binaries_file()

    def _get_binary_versions(self) -> dict[str, str]:
        """Returns versions of downloaded binaries

        Returns
        -------
        dict[str, str]
            versions of downloaded binaries
        """

        if self._binaries_file_contents is None:
            self._binaries_file_contents = self.get_binaries_file_contents_with_default()

        return self._binaries_file_contents

    def _save_binaries_file(self):
        """Stores versions of downloaded binaries in a configuration file"""

        configuration_manager.get_cli_data_directory_path().mkdir(exist_ok=True)

        with open(self.get_binaries_file_path(), "w") as binaries_file:
            json.dump(
                self._get_binary_versions(),
                binaries_file,
                indent="\t",
                sort_keys=True,
            )


binaries_manager = BinariesManager()
