#  Copyright 2024 IBM Corporation
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

import cpo.commands.adm.credentials.store
import cpo.config
import cpo.lib.click.utils

from cpo.cpo import cli


class TestStoreCommand(unittest.TestCase):
    def test_store(self):
        """Tests that cpo adm credentials store creates credentials.json"""

        credentials_file_path = pathlib.Path(tempfile.gettempdir()) / "credentials.json"

        if credentials_file_path.exists():
            os.remove(credentials_file_path)

        cpo.config.configuration_manager.get_credentials_file_path = unittest.mock.MagicMock(
            return_value=credentials_file_path
        )

        # check that key-value pairs were added to credentials.json
        runner = click.testing.CliRunner()
        runner.invoke(
            cli,  # type: ignore
            [
                "adm",
                "credentials",
                "store",
                "--credentials-key",
                "credentials_key",
                "--credentials-value",
                "credentials_value",
            ],
        )

        default_map = self._load_credentials_file(credentials_file_path)

        self.assertIn("credentials_key", default_map)
        self.assertEqual(default_map["credentials_key"], "credentials_value")

        # check that key-value pairs were removed from credentials.json
        runner = click.testing.CliRunner()
        runner.invoke(
            cli,  # type: ignore
            [
                "adm",
                "credentials",
                "rm",
                "--credentials-key",
                "credentials_key",
            ],
        )

        default_map = self._load_credentials_file(credentials_file_path)

        self.assertNotIn("credentials_key", default_map)

    def _load_credentials_file(self, credentials_file_path: pathlib.Path):
        json = cpo.lib.click.utils.create_default_map_from_json_file(credentials_file_path)

        self.assertIn("default_map", json)

        default_map = json["default_map"]

        return default_map


if __name__ == "__main__":
    unittest.main()
