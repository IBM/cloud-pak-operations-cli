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

import json
import pathlib

from typing import Any, Dict, Optional

import cpo

from cpo.lib.error import DataGateCLIException


class ConfigurationManager:
    """Manages the CLI configuration"""

    def are_fyre_commands_hidden(self) -> bool:
        """Returns whether FYRE options shall be displayed in help texts. The
        functionality is always usable.

        Returns
        -------
        bool
            true, if FYRE options shall be hidden in help texts
        """

        return not self.get_bool_config_value("fyre_commands", False)

    def are_nuclear_commands_hidden(self) -> bool:
        """Returns whether nuclear options shall be displayed in help texts. The
        functionality is always usable.

        Returns
        -------
        bool
            true, if nuclear options shall be hidden in help texts
        """

        return not self.get_bool_config_value("nuclear_commands", False)

    def get_bool_config_value(self, key: str, default_value: bool) -> bool:
        """Gets the value for a given key from the settings file

        Parameters
        ----------
        key
            name of the key of the value to get
        default_value
            default value to use if key cannot be found in the settings file
        """

        result = default_value

        if self.get_settings_file_path().exists():
            settings = json.loads(self.get_settings_file_path().read_text())

            if key in settings:
                value = str(settings[key])

                if value.lower() in ConfigurationManager._supported_true_boolean_values:
                    result = True
                elif value.lower() in ConfigurationManager._supported_false_boolean_values:
                    result = False
                else:
                    raise DataGateCLIException(
                        f"Expected value of configuration parameter '{key}' must be a boolean of the form "
                        f"[{', '.join(ConfigurationManager._supported_true_boolean_values)}] or "
                        f"[{', '.join(ConfigurationManager._supported_false_boolean_values)}] but found "
                        f"'{value}'."
                    )

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

    def get_bin_directory_path(self) -> pathlib.Path:
        """Returns the path of the binaries directory

        Returns
        -------
        pathlib.Path
            path of the binaries directory
        """

        return self.get_cli_data_directory_path() / "bin"

    def get_credentials_file_path(self) -> pathlib.Path:
        """Returns the path of the credentials file

        Returns
        -------
        pathlib.Path
            path of the credentials file
        """

        return self.get_cli_data_directory_path() / "credentials.json"

    def get_cli_data_directory_path(self) -> pathlib.Path:
        """Returns the path of the CLI data directory

        Returns
        -------
        pathlib.Path
            path of the CLI data directory
        """

        return self.get_home_directory_path() / ".cpo"

    def get_settings_file_path(self) -> pathlib.Path:
        """Returns the path of the settings file

        Returns
        -------
        str
            path of the settings file
        """

        return self.get_cli_data_directory_path() / "settings.json"

    def get_home_directory_path(self) -> pathlib.Path:
        return pathlib.Path.home()

    def get_root_package_path(self) -> pathlib.Path:
        """Returns the path of the root package

        Returns
        -------
        pathlib.Path
            path of the root package
        """

        return pathlib.Path(cpo.__file__).parent

    def get_value_from_credentials_file(self, key: str) -> Optional[str]:
        """Returns the value corresponding to the given key stored in the
        credentials file

        Parameters
        ----------
        key
            key for which the corresponding value shall be returned

        Returns
        -------
            Optional[str]
                value corresponding to the given key or None if the key does not exist
        """

        credentials_file_contents = self.read_credentials_file_contents()
        result: Optional[str] = None

        if (credentials_file_contents is not None) and (key in credentials_file_contents):
            result = credentials_file_contents[key]

        return result

    def read_credentials_file_contents(self) -> Optional[Any]:
        """Returns the contents of the credentials file

        Returns
        -------
            Optional[str]
                contents of the credentials file or none of the credentials file does
                not exist or is empty
        """

        credentials_file_path = self.get_credentials_file_path()
        result: Optional[str] = None

        if credentials_file_path.exists() and (credentials_file_path.stat().st_size != 0):
            with open(credentials_file_path) as json_file:
                result = json.load(json_file)

        return result

    def set_bool_config_value(self, key: str, value: str):
        """Sets a given key:value pair in the settings file

        Parameters
        ----------
        key
            name of the key to set
        value
            value to be set for key
        """

        if value.lower() not in (
            ConfigurationManager._supported_true_boolean_values + ConfigurationManager._supported_false_boolean_values
        ):
            raise DataGateCLIException(
                f"Passed value '{value}' for '{key}' must be a boolean of the form "
                f"[{', '.join(ConfigurationManager._supported_true_boolean_values)}] or "
                f"[{', '.join(ConfigurationManager._supported_false_boolean_values)}]."
            )

        settings = {}

        if self.get_settings_file_path().exists():
            settings = json.loads(self.get_settings_file_path().read_text())

            settings[key] = value
        else:
            settings = {key: value}

        with open(self.get_settings_file_path(), "w+") as f:
            f.write(json.dumps(settings, indent="\t", sort_keys=True))

    def store_credentials(
        self,
        credentials_to_be_stored: Dict[str, Any],
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

        credentials: Optional[Dict[Any, Any]] = None
        credentials_file_path = self.get_credentials_file_path()

        if credentials_file_path.exists():
            with open(credentials_file_path) as credentials_file:
                credentials = json.load(credentials_file)

                if credentials is None:
                    raise TypeError()
        else:
            credentials = {}

        for key, value in credentials_to_be_stored.items():
            if value is not None:
                if value != "":
                    credentials[key] = value
                else:
                    credentials.pop(key)

        self.get_cli_data_directory_path().mkdir(exist_ok=True)

        with open(credentials_file_path, "w") as credentials_file:
            json.dump(credentials, credentials_file, indent="\t", sort_keys=True)

    _supported_false_boolean_values = ["disable", "disabled", "false", "inactive", "no"]
    _supported_true_boolean_values = ["active", "enable", "enabled", "true", "yes"]
