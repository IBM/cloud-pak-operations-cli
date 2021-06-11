import json
import unittest

from pathlib import Path
from unittest.mock import patch

from dg.lib.ibmcloud.openshift import get_latest_supported_openshift_version


class TestIBMCloudOpenShift(unittest.TestCase):
    @patch(
        "dg.lib.ibmcloud.openshift._get_oc_versions_as_json",
        return_value=json.loads((Path(__file__).parent / "dependencies/ibmcloud_oc_versions.json").read_text()),
    )
    def test_get_openshift_version(self, test_mock):
        result = get_latest_supported_openshift_version()

        self.assertEqual("4.5.18_openshift", result)
