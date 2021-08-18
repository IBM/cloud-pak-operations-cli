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

import os
import pathlib
import tempfile
import unittest
import unittest.mock

import click.testing

import dg.commands.adm.store_credentials
import dg.config
import dg.lib.click.utils

from dg.dg import cli


class TestStoreCredentialsCommand(unittest.TestCase):
    def test_store_credentials(self):
        """Tests that dg adm store-credentials creates credentials.json"""

        dg_credentials_file_path = pathlib.Path(tempfile.gettempdir()) / "credentials.json"

        if dg_credentials_file_path.exists():
            os.remove(dg_credentials_file_path)

        dg.config.data_gate_configuration_manager.get_dg_credentials_file_path = unittest.mock.MagicMock(
            return_value=dg_credentials_file_path
        )

        # check that key-value pairs were added to credentials.json
        runner = click.testing.CliRunner()
        runner.invoke(
            cli,
            [
                "adm",
                "store-credentials",
                "--artifactory-api-key",
                "artifactory_api_key",
                "--artifactory-user-name",
                "artifactory_user_name",
                "--ibm-cloud-api-key",
                "ibm_cloud_api_key",
            ],
        )

        default_map = self._load_credentials_file(dg_credentials_file_path)

        self.assertIn("artifactory_api_key", default_map)
        self.assertIn("artifactory_user_name", default_map)
        self.assertIn("ibm_cloud_api_key", default_map)
        self.assertEqual(default_map["artifactory_api_key"], "artifactory_api_key")
        self.assertEqual(default_map["artifactory_user_name"], "artifactory_user_name")
        self.assertEqual(default_map["ibm_cloud_api_key"], "ibm_cloud_api_key")

        # check that key-value pairs were removed from credentials.json
        runner = click.testing.CliRunner()
        runner.invoke(
            cli,
            [
                "adm",
                "store-credentials",
                "--artifactory-api-key",
                "",
                "--artifactory-user-name",
                "",
                "--ibm-cloud-api-key",
                "",
            ],
        )

        default_map = self._load_credentials_file(dg_credentials_file_path)

        self.assertNotIn("artifactory_api_key", default_map)
        self.assertNotIn("artifactory_user_name", default_map)
        self.assertNotIn("ibm_cloud_api_key", default_map)

    def _load_credentials_file(self, dg_credentials_file_path: pathlib.Path):
        json = dg.lib.click.utils.create_default_map_from_json_file(dg_credentials_file_path)

        self.assertIn("default_map", json)

        default_map = json["default_map"]

        return default_map


if __name__ == "__main__":
    unittest.main()
