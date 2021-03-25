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

from dg.config.cluster_credentials_manager import cluster_credentials_manager
from dg.dg import cli


class TestVersionCommand(unittest.TestCase):
    def test_logging_in_fails(self):
        """Tests that dg fyre login fails if wrong credentials are used"""

        dg_clusters_file_path = pathlib.Path(tempfile.gettempdir()) / "clusters.json"

        if dg_clusters_file_path.exists():
            os.remove(dg_clusters_file_path)

        cluster_credentials_manager.get_dg_clusters_file_path = unittest.mock.MagicMock(
            return_value=dg_clusters_file_path
        )

        runner = click.testing.CliRunner()
        result = runner.invoke(
            cli,
            [
                "fyre",
                "login",
                "--fyre-api-key",
                "fyre_api_key",
                "--fyre-user-name",
                "fyre_user_name",
            ],
        )

        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, "Error: Failed to log in to FYRE (failed authentication)\n")


if __name__ == "__main__":
    unittest.main()
