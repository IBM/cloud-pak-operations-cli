#  Copyright 2021, 2026 IBM Corporation
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

import pathlib
import unittest

from unittest.mock import patch

from cpo.lib.ibmcloud.ibm_cloud_api_manager import IBMCloudAPIManager
from cpo.utils.process import ProcessResult


class TestIBMCloudCommon(unittest.TestCase):
    @patch.object(
        IBMCloudAPIManager,
        "execute_ibmcloud_command",
        lambda self, args, capture_output=False, check=True, print_captured_output=False: ProcessResult(
            command=[],
            stderr=[],
            stdout=[(pathlib.Path(__file__).parent / "dependencies/ibmcloud_oc_cluster_status_1.json").read_text()],
            return_code=0,
        ),
    )
    def test_is_cluster_ready_false(self):
        ibm_cloud_api_manager = IBMCloudAPIManager()

        self.assertFalse(ibm_cloud_api_manager.get_cluster_status("cluster").is_ready())

    @patch.object(
        IBMCloudAPIManager,
        "execute_ibmcloud_command",
        lambda self, args, capture_output=False, check=True, print_captured_output=False: ProcessResult(
            command=[],
            stderr=[],
            stdout=[(pathlib.Path(__file__).parent / "dependencies/ibmcloud_oc_cluster_status_2.json").read_text()],
            return_code=0,
        ),
    )
    def test_is_cluster_ready_true(self):
        ibm_cloud_api_manager = IBMCloudAPIManager()

        self.assertTrue(ibm_cloud_api_manager.get_cluster_status("cluster").is_ready())


if __name__ == "__main__":
    unittest.main()
