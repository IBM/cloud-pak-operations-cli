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

import ipaddress
import unittest

import cpo.lib.fyre.utils.network
import cpo.utils.network


class TestNetworkUtilities(unittest.TestCase):
    def test_get_private_ip_address_of_infrastructure_node(self):
        """Tests cpo.utils.network.is_hostname_localhost()"""

        hostname_result = "9.0.0.1 10.0.0.1"
        ipv4_addresses = cpo.utils.network.parse_hostname_result(hostname_result)

        self.assertEqual(
            cpo.lib.fyre.utils.network.get_private_ip_address_of_infrastructure_node(ipv4_addresses),
            ipaddress.ip_address("10.0.0.1"),
        )


if __name__ == "__main__":
    unittest.main()
