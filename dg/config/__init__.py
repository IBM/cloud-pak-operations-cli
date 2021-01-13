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


class DataGateConfigurationManager:
    """Manages the Data Gate CLI configuration"""

    supported_true_boolean_values = ["true", "yes", "enable", "enabled", "active"]
    supported_false_boolean_values = ["false", "no", "disable", "disabled", "inactive"]

    def get_current_credentials(self) -> ContextData:
        """Returns user and current cluster credentials

        Returns
        -------
        pathlib.Path
            path of the directory containing required non-Python files
        """

        return self.get_root_package_path() / "deps"

    def get_dg_directory_path(self) -> pathlib.Path:
        """Return the path of the Data Gate CLI directory

        Returns
        -------
        pathlib.Path
            path of the Data Gate CLI directory
        """

        return self.get_home_directory_path() / ".dg"

    def get_dg_bin_directory_path(self) -> pathlib.Path:
        """Returns the path of the binaries directory

        Returns
        -------
        pathlib.Path
            path of the binaries directory
        """

        return self.get_dg_directory_path() / "bin"

    def get_dg_credentials_file_path(self) -> pathlib.Path:
        """Returns the path of the credentials file

        Returns
        -------
        pathlib.Path
            path of the credentials file
        """

        return self.get_dg_directory_path() / "credentials.json"

    def get_home_directory_path(self) -> pathlib.Path:
        return pathlib.Path.home()

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

    def are_fyre_commands_hidden(self) -> bool:
        """Returns whether FYRE options shall be displayed in help texts. The
        functionality is always usable.

        Returns
        -------
        bool
            true, if FYRE options shall be hidden in help texts
            false if not
        """

        return not self.get_dg_bool_config_value("fyre_commands", False)

    def are_nuclear_commands_hidden(self) -> bool:
        """Returns whether nuclear options shall be displayed in help texts. The
        functionality is always usable.

        Returns
        -------
        bool
            true, if nuclear options shall be hidden in help texts
            false if not
        """

        return not self.get_dg_bool_config_value("nuclear_commands", False)

    def get_dg_bool_config_value(self, key: str, default_value: bool) -> bool:
        """Get the value for a given key from the dg configuration file

        Parameters
        ----------
        key
            name of the key of the value to get

        default_value
            default_value value to use if key cannot be found in the config file
        """
        result = default_value

        if self.get_dg_settings_file_path().exists():
            settings = json.loads(self.get_dg_settings_file_path().read_text())

            if key in settings:
                value = str(settings[key])

                if value.lower() in self.supported_true_boolean_values:
                    result = True
                elif value.lower() in self.supported_false_boolean_values:
                    result = False
                else:
                    raise Exception(
                        f"Expected value of configuration parameter '{key}' must be a boolean of the form "
                        f"[{', '.join(self.supported_true_boolean_values)}] or "
                        f"[{', '.join(self.supported_false_boolean_values)}] but found '{value}'."
                    )

        return result

    def set_dg_bool_config_value(self, key: str, value: str):
        """Set a given key:value pair in the dg configuration file

        Parameters
        ----------
        key
            name of the key to set

        value
            value to be set for key
        """

        if (
            value.lower() not in (self.supported_true_boolean_values + self.supported_false_boolean_values)
        ):
            raise Exception(
                f"Passed value '{value}' for '{key}' must be a boolean of the form "
                f"[{', '.join(self.supported_true_boolean_values)}] or "
                f"[{', '.join(self.supported_false_boolean_values)}]."
            )

        settings = {}
        if self.get_dg_settings_file_path().exists():
            settings = json.loads(self.get_dg_settings_file_path().read_text())

            settings[key] = value
        else:
            settings = {key: value}

        with open(self.get_dg_settings_file_path(), "w+") as f:
            f.write(json.dumps(settings, indent=4))


data_gate_configuration_manager = DataGateConfigurationManager()
