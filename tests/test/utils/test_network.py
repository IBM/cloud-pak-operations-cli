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

import cpo.utils.network


class TestNetworkUtilities(unittest.TestCase):
    def test_is_hostname_localhost(self):
        """Tests cpo.utils.network.is_hostname_localhost()"""

        self.assertTrue(cpo.utils.network.is_hostname_localhost("localhost"))
        self.assertTrue(cpo.utils.network.is_hostname_localhost("127.0.0.1"))
        self.assertFalse(cpo.utils.network.is_hostname_localhost("127.0.0.254"))

    def test_parse_hostname_result(self):
        """Tests cpo.utils.network()"""

        hostname_result = "9.0.0.1 10.0.0.1"
        ipv4_addresses = cpo.utils.network.parse_hostname_result(hostname_result)

        self.assertEqual(len(ipv4_addresses), 2)
        self.assertEqual(str(ipv4_addresses[0]), "9.0.0.1")
        self.assertEqual(str(ipv4_addresses[1]), "10.0.0.1")


if __name__ == "__main__":
    unittest.main()
