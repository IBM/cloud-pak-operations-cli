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

from cpo.lib.error import DataGateCLIException
from cpo.lib.fyre.data.ocpplus_cluster_specification import (
    HAProxyTimoutSettings,
)
from cpo.lib.fyre.types.ocp_post_request import (
    HAProxyTimeoutData,
    OCPPostRequest,
)


class TestHAProxyTimoutSettings(unittest.TestCase):
    def test_empty_haproxy_settings(self):
        """Tests that an HAProxyTimoutSettings object constructed without
        arguments does not change the passed dictionary when calling
        add_settings_to_dict()"""

        ocp_post_request: OCPPostRequest = {}

        ha_proxy_timout_settings = HAProxyTimoutSettings()
        ha_proxy_timout_settings.add_settings_to_dict(ocp_post_request)

        self.assertNotIn("haproxy", ocp_post_request)

    def test_non_empty_haproxy_settings(self):
        """Tests that an HAProxyTimoutSettings object constructed with one more
        arguments adds expected values to the passed dictionary when calling
        add_settings_to_dict()"""

        ocp_post_request: OCPPostRequest = {}
        ha_proxy_timout_settings = HAProxyTimoutSettings("10s", "1m", "10s", "10s", "10s", "1m", "1m")

        ha_proxy_timout_settings.add_settings_to_dict(ocp_post_request)

        self.assertIn("haproxy", ocp_post_request)

        if "haproxy" in ocp_post_request:
            haproxy = ocp_post_request["haproxy"]

            self.assertEqual(len(haproxy), 1)
            self.assertIn("timeout", haproxy)

            ha_proxy_timout_settings_dict = ocp_post_request["haproxy"]["timeout"]

            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "check", "10s")
            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "client", "1m")
            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "connect", "10s")
            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "http-keep-alive", "10s")
            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "http-request", "10s")
            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "queue", "1m")
            self._test_ha_proxy_timout_settings_dict(ha_proxy_timout_settings_dict, "server", "1m")

    def test_invalid_string_format(self):
        """Tests that constructing an HAProxyTimoutSettings object with an
        invalidly formatted string raises an exception"""

        self.assertRaisesRegex(
            DataGateCLIException,
            "Invalid string format: 10",
            HAProxyTimoutSettings,
            "10",
        )

    def _test_ha_proxy_timout_settings_dict(
        self, ha_proxy_timout_settings_dict: HAProxyTimeoutData, key: str, value: str
    ):
        self.assertIn(key, ha_proxy_timout_settings_dict)
        self.assertEqual(ha_proxy_timout_settings_dict[key], value)


if __name__ == "__main__":
    unittest.main()
