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

import json
import pathlib
import sys

from typing import Any, Union

import dg.config.cluster_credentials_manager

ContextData = dict[str, Any]


class DataGateConfigurationManager:
    """Manages the Data Gate CLI configuration"""

    def get_current_credentials(self) -> ContextData:
        """Returns user and current cluster credentials

        Returns
        -------
        ContextData
            user and current cluster credentials
        """

        dg_credentials_file_path = self.get_dg_credentials_file_path()
        result: ContextData

        if dg_credentials_file_path.exists() and (
            dg_credentials_file_path.stat().st_size != 0
        ):
            with open(dg_credentials_file_path) as json_file:
                result = json.load(json_file)
        else:
            result = {}

        current_cluster = (
            dg.config.cluster_credentials_manager.cluster_credentials_manager.get_current_cluster()
        )

        if current_cluster is not None:
            result.update(current_cluster.get_cluster_data())
            result["server"] = current_cluster.get_server()

        return result

    def get_deps_directory_path(self) -> pathlib.Path:
        """Returns the path of the directory containing required non-Python
        files

        Returns
        -------
        pathlib.Path
            path of the directory containing required non-Python files
        """

        return self.get_root_package_path() / "deps"

    def get_dg_bin_directory_path(self) -> pathlib.Path:
        """Returns the path of the binaries directory

        Returns
        -------
        str
            path of the binaries directory
        """

        return pathlib.Path.home() / ".dg" / "bin"

    def get_dg_credentials_file_path(self) -> pathlib.Path:
        """Returns the path of the credentials file

        Returns
        -------
        str
            path of the credentials file
        """

        return pathlib.Path.home() / ".dg" / "credentials.json"

    def get_ibmcloud_cli_path(self) -> pathlib.Path:
        """Returns the path to the IBM Cloud CLI

        Returns
        -------
        pathlib.Path
            path to the IBM Cloud CLI
        """

        return self.get_dg_bin_directory_path() / "ibmcloud"

    def get_oc_cli_path(self) -> pathlib.Path:
        """Returns the path to the OpenShift Container Platform CLI

        Returns
        -------
        pathlib.Path
            path to the OpenShift Container Platform CLI
        """

        return self.get_dg_bin_directory_path() / "oc"

    def get_root_package_path(self) -> pathlib.Path:
        """Returns the path of the root package

        Returns
        -------
        pathlib.Path
            path of the root package
        """

        return pathlib.Path(sys.modules["dg"].__file__).parent

    def get_value_from_credentials_file(self, key: str) -> Union[str, None]:
        """Returns the value corresponding to the given key stored in the
        credentials file

        Parameters
        ----------
        key
            key for which the corresponding value shall be returned

        Returns
        -------
            Union[str, None]
                value corresponding to the given key or None if the key does not exist
        """

        credentials_file_contents = self.read_credentials_file_contents()
        result: Union[str, None] = None

        if credentials_file_contents is not None:
            if key in credentials_file_contents:
                result = credentials_file_contents[key]

        return result

    def read_credentials_file_contents(self) -> Union[Any, None]:
        """Returns the contents of the credentials file

        Returns
        -------
            Union[str, None]
                contents of the credentials file or none of the credentials file does
                not exist or is empty
        """

        dg_credentials_file_path = self.get_dg_credentials_file_path()
        result: Union[str, None] = None

        if dg_credentials_file_path.exists() and (
            dg_credentials_file_path.stat().st_size != 0
        ):
            with open(dg_credentials_file_path) as json_file:
                result = json.load(json_file)

        return result

    def store_credentials(
        self,
        credentials_to_be_stored: dict[str, Any],
    ):
        """Stores credentials in a configuration file

        Parameters
        ----------
        credentials_to_be_stored
            dictionary containing key-value pairs to be stored (key-value pairs
            whose value is None are ignored)
        """

        if all(value is None for value in credentials_to_be_stored.values()):
            return

        credentials: Union[dict[Any, Any], None] = None
        dg_credentials_file_path = self.get_dg_credentials_file_path()

        if dg_credentials_file_path.exists():
            with open(dg_credentials_file_path) as credentials_file:
                credentials = json.load(credentials_file)
        else:
            credentials = {}

        for key, value in credentials_to_be_stored.items():
            if value is not None:
                if value != "":
                    credentials[key] = value
                else:
                    credentials.pop(key)

        with open(dg_credentials_file_path, "w") as credentials_file:
            json.dump(credentials, credentials_file, indent="\t", sort_keys=True)

    def get_dg_settings_file_path(self) -> pathlib.Path:
        """Returns the path of the settings file

        Returns
        -------
        str
            path of the settings file
        """

        return pathlib.Path.home() / ".dg" / "settings.json"

    def show_fyre_options(self) -> bool:
        """Returns true if Fyre options should be shown

        Returns
        -------
        bool
            true if options should be shown
            false if not
        """

        result = False

        if self.get_dg_settings_file_path().exists():
            settings = json.loads(self.get_dg_settings_file_path().read_text())

            if "show_fyre" in settings and settings["show_fyre"]:
                result = True

        return result

    def show_ibmcloud_nuclear_options(self) -> bool:
        """Returns true if IBM Cloud nuclear options should be shown

        Returns
        -------
        bool
            true if options should be shown
            false if not
        """

        result = False

        if self.get_dg_settings_file_path().exists():
            settings = json.loads(self.get_dg_settings_file_path().read_text())

            if "show_ibmcloud_nuclear" in settings and settings["show_ibmcloud_nuclear"]:
                result = True

        return result


data_gate_configuration_manager = DataGateConfigurationManager()
