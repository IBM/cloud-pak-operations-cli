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

from unittest.mock import patch

import click.testing

import dg.config
import dg.utils.file
import dg.utils.operating_system

from dg.dg import cli
from dg.lib.download_manager.plugins.ibm_cloud_terraform_provider_plugin import (
    IBMCloudTerraformProviderPlugIn,
)


class TestDownloadDependencies(unittest.TestCase):
    def add_os_specific_executable_extension(self, executable_name: str) -> str:
        operating_system = dg.utils.operating_system.get_operating_system()

        if operating_system == dg.utils.operating_system.OperatingSystem.WINDOWS:
            executable_name += ".exe"

        return executable_name

    def check_executable_exists(self, dg_bin_directory_path: pathlib.Path, executable_name: str):
        self.assertTrue(
            (pathlib.Path(dg_bin_directory_path) / self.add_os_specific_executable_extension(executable_name)).exists()
        )

    @patch(
        "dg.config.binaries_manager.data_gate_configuration_manager.get_home_directory_path",
        return_value=pathlib.Path(tempfile.gettempdir()),
    )
    def test_command(self, test_mock):
        """Tests that dg adm download-dependencies downloads
        dependencies"""

        dg_bin_directory_path = dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()
        terraform_plugins_directory_path = IBMCloudTerraformProviderPlugIn().get_terraform_plugins_directory_path()

        for entry in dg_bin_directory_path.glob("*"):
            if entry.is_file():
                os.remove(entry)

        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["adm", "download-dependencies"])

        self.assertEqual(result.exit_code, 0)
        self.assertGreaterEqual(
            len(list(terraform_plugins_directory_path.glob("terraform-provider-ibm*"))),
            1,
        )

        self.check_executable_exists(dg_bin_directory_path, "ibmcloud")
        self.check_executable_exists(dg_bin_directory_path, "oc")
        self.check_executable_exists(dg_bin_directory_path, "terraform")


if __name__ == "__main__":
    unittest.main()
