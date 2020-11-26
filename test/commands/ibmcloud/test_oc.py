import unittest

from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from dg.lib.ibmcloud.oc import get_latest_supported_openshift_version


class TestIBMCloudOpenShift(unittest.TestCase):
    @patch(
        "dg.commands.ibmcloud.common.execute_ibmcloud_command_with_check",
        return_value=CompletedProcess(
            args="",
            stdout=(
                Path(__file__).parent / "dependencies/ibmcloud_oc_versions.json"
            ).read_text(),
            returncode=0,
        ),
    )
    def test_get_openshift_version(self, test_mock):
        result = get_latest_supported_openshift_version()

        self.assertEqual("4.5.18_openshift", result)
