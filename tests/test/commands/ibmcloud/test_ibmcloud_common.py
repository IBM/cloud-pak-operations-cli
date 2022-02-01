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

import unittest

from pathlib import Path
from unittest.mock import patch

from cpo.lib.ibmcloud.iam import api_key_exists, generate_api_key
from cpo.lib.ibmcloud.install import _get_cp4d_version_locator
from cpo.lib.ibmcloud.status import get_cluster_status
from cpo.lib.ibmcloud.vlan_manager import VLANManager
from cpo.utils.process import ProcessResult


class TestIBMCloudCommon(unittest.TestCase):
    @patch(
        "cpo.lib.ibmcloud.iam.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=(Path(__file__).parent / "dependencies/ibmcloud_generate_api_key.json").read_text(),
            return_code=0,
        ),
    )
    def test_generate_api_key(self, test_mock):
        result = generate_api_key()
        self.assertEqual("3O_fwBGvkWrug5VrI0aQJwRPuqX1Yb7_MtSTZK_qFthb", result)

    @patch(
        "cpo.lib.ibmcloud.iam.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=(Path(__file__).parent / "dependencies/ibmcloud_api_keys.json").read_text(),
            return_code=0,
        ),
    )
    def test_api_key_exists(self, test_mock):
        self.assertTrue(api_key_exists("cpo.api.key"))
        self.assertTrue(api_key_exists("cpo.api.key.2"))
        self.assertFalse(api_key_exists("cpo.api.key.3"))

    @patch(
        "cpo.lib.ibmcloud.vlan_manager.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=(Path(__file__).parent / "dependencies/ibmcloud_list_vlans.json").read_text(),
            return_code=0,
        ),
    )
    def test_get_default_public_vlan(self, test_mock):
        vlan_manager = VLANManager("sjc03")

        self.assertEqual("2734440", vlan_manager.default_public_vlan)

    @patch(
        "cpo.lib.ibmcloud.vlan_manager.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=(Path(__file__).parent / "dependencies/ibmcloud_list_vlans.json").read_text(),
            return_code=0,
        ),
    )
    def test_get_default_private_vlan(self, test_mock):
        vlan_manager = VLANManager("sjc03")

        self.assertEqual("2734442", vlan_manager.default_private_vlan)

    @patch(
        "cpo.lib.ibmcloud.status.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=(Path(__file__).parent / "dependencies/ibmcloud_oc_cluster_status.json").read_text(),
            return_code=0,
        ),
    )
    def test_is_cluster_ready_false(self, test_mock):
        self.assertFalse(get_cluster_status("datagate.test").is_ready())

    @patch(
        "cpo.lib.ibmcloud.status.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=(Path(__file__).parent / "dependencies/ibmcloud_oc_cluster_status_2.json").read_text(),
            return_code=0,
        ),
    )
    def test_is_cluster_ready_true(self, test_mock):
        self.assertTrue(get_cluster_status("datagate.test").is_ready())

    @patch(
        "cpo.lib.ibmcloud.install.execute_ibmcloud_command",
        return_value=ProcessResult(
            stderr="",
            stdout=Path(Path(__file__).parent / "dependencies/ibmcloud_catalog_search_pak.json").read_text(),
            return_code=0,
        ),
    )
    def test_get_cp4d_version_locator(self, test_mock):
        self.assertEqual(
            _get_cp4d_version_locator("3.0.1"),
            "1082e7d2-5e2f-0a11-a3bc-f88a8e1931fc.bac1d34a-d912-45e4-bc81-10cd7b94bcc1-global",
        )


if __name__ == "__main__":
    unittest.main()
