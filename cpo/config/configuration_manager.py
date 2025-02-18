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

import json
import os
import pathlib

from typing import Any, Type, TypeVar

import cpo

from cpo.utils.error import CloudPakOperationsCLIException

T = TypeVar("T")


class ConfigurationManager:
    """Manages the CLI configuration"""

    def get_config_value(self, key: str, type: Type[T], default_value: T | None = None) -> T:
        """Gets the value for the given key from the settings file

        Parameters
        ----------
        key
            name of the key of the value to get
        default_value
            default value to use if key cannot be found in the settings file
        """

        result = default_value

        if self.get_settings_file_path().exists():
            with open(self.get_settings_file_path()) as json_file:
                settings = json.load(json_file)

            if key in settings:
                value = settings[key]

                if not isinstance(value, type):
                    raise CloudPakOperationsCLIException(f"Configuration option '{key}' is not of expected type {type}")

                result = value

        if result is None:
            raise CloudPakOperationsCLIException(
                f"Configuration option '{key}' is not set and no default value was provided"
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

    def get_ibmcloud_data_directory_path(self) -> pathlib.Path:
        """Returns the path of the IBM Cloud CLI data directory

        Returns
        -------
        pathlib.Path
            path of the IBM Cloud CLI data directory
        """

        return self.get_cli_data_directory_path() / ".bluemix"

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

    def get_value_from_credentials_file(self, key: str) -> str | None:
        """Returns the value corresponding to the given key stored in the
        credentials file

        Parameters
        ----------
        key
            key for which the corresponding value shall be returned

        Returns
        -------
            str | None
                value corresponding to the given key or None if the key does not exist
        """

        credentials_file_contents = self.read_credentials_file_contents()
        result: str | None = None

        if (credentials_file_contents is not None) and (key in credentials_file_contents):
            result = credentials_file_contents[key]

        return result

    def read_credentials_file_contents(self) -> Any | None:
        """Returns the contents of the credentials file

        Returns
        -------
            str | None
                contents of the credentials file or none of the credentials file does
                not exist or is empty
        """

        credentials_file_path = self.get_credentials_file_path()
        result: str | None = None

        if credentials_file_path.exists() and (credentials_file_path.stat().st_size != 0):
            with open(credentials_file_path) as json_file:
                result = json.load(json_file)

        return result

    def set_bool_config_value(self, key: str, value: bool):
        """Sets a given key-value pair in the settings file

        Parameters
        ----------
        key
            name of the key to set
        value
            value to be set for key
        """

        if self.get_settings_file_path().exists():
            settings = json.loads(self.get_settings_file_path().read_text())
            settings[key] = value
        else:
            settings = {key: value}

        with open(self.get_settings_file_path(), "w+") as f:
            f.write(json.dumps(settings, indent="\t", sort_keys=True))

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

        credentials: dict[Any, Any] | None = None
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
                    credentials.pop(key, None)

        self.get_cli_data_directory_path().mkdir(exist_ok=True)

        with open(credentials_file_path, "w") as credentials_file:
            json.dump(credentials, credentials_file, indent="\t", sort_keys=True)

    def unset_config_value(self, key: str):
        """Unsets the given key in the settings file

        Parameters
        ----------
        key
            name of the key to be deleted
        """

        if self.get_settings_file_path().exists():
            settings: dict[str, Any] = json.loads(self.get_settings_file_path().read_text())

            if settings.pop(key, None) is not None:
                if len(settings) == 0:
                    os.remove(self.get_settings_file_path())
                else:
                    with open(self.get_settings_file_path(), "w+") as f:
                        f.write(json.dumps(settings, indent="\t", sort_keys=True))
