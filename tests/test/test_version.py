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

import importlib.metadata
import re as regex
import unittest

import click.testing

from cpo import distribution_package_name
from cpo.cpo import cli


class TestVersionCommand(unittest.TestCase):
    def test_command(self):
        """Tests that cpo --version returns a semantic version number"""

        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["--version"])

        self.assertEqual(result.exit_code, 0)

        search_result = regex.match(
            f"{importlib.metadata.metadata(distribution_package_name)['Summary']} \\d+\\.\\d+\\.\\d+", result.output
        )

        self.assertNotEqual(search_result, None)


if __name__ == "__main__":
    unittest.main()
