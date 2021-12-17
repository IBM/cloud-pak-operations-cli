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

import json
import unittest

from pathlib import Path
from unittest.mock import patch

from cpo.lib.ibmcloud.openshift import get_latest_supported_openshift_version


class TestIBMCloudOpenShift(unittest.TestCase):
    @patch(
        "cpo.lib.ibmcloud.openshift._get_oc_versions_as_json",
        return_value=json.loads((Path(__file__).parent / "dependencies/ibmcloud_oc_versions.json").read_text()),
    )
    def test_get_openshift_version(self, test_mock):
        result = get_latest_supported_openshift_version()

        self.assertEqual("4.5.18_openshift", result)
