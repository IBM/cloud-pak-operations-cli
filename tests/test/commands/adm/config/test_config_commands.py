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


class TestConfigCommands(unittest.TestCase):
    def test_set_unset(self):
        """Tests 'cpo adm config set-bool' and 'cpo adm config unset'"""

        settings_file_path = pathlib.Path(tempfile.gettempdir()) / "settings.json"

        if settings_file_path.exists():
            os.remove(settings_file_path)

        cpo.config.configuration_manager.get_settings_file_path = unittest.mock.MagicMock(
            return_value=settings_file_path
        )

        # check that key-value pairs were added to settings.json
        runner = click.testing.CliRunner()
        runner.invoke(
            cli,  # type: ignore
            [
                "adm",
                "config",
                "set-bool",
                "--key",
                "key",
                "--value",
                "true",
            ],
        )

        value = cpo.config.configuration_manager.get_config_value("key", bool)

        self.assertEqual(value, True)

        # check that key-value pairs were removed from settings.json
        runner = click.testing.CliRunner()
        runner.invoke(
            cli,  # type: ignore
            [
                "adm",
                "config",
                "unset",
                "--key",
                "key",
            ],
        )

        value = cpo.config.configuration_manager.get_config_value("key", bool, False)

        self.assertEqual(value, False)
        self.assertFalse(settings_file_path.exists())


if __name__ == "__main__":
    unittest.main()
