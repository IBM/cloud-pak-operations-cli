import unittest

import dg.utils.network


class TestNetworkUtilities(unittest.TestCase):
    def test_is_hostname_localhost(self):
        """Tests dg.utils.network.is_hostname_localhost()"""

        self.assertTrue(dg.utils.network.is_hostname_localhost("localhost"))
        self.assertTrue(dg.utils.network.is_hostname_localhost("127.0.0.1"))
        self.assertFalse(dg.utils.network.is_hostname_localhost("127.0.0.254"))

    def test_parse_hostname_result(self):
        """Tests dg.utils.network()"""

        hostname_result = "9.0.0.1 10.0.0.1"
        ipv4_addresses = dg.utils.network.parse_hostname_result(hostname_result)

        self.assertEqual(len(ipv4_addresses), 2)
        self.assertEqual(str(ipv4_addresses[0]), "9.0.0.1")
        self.assertEqual(str(ipv4_addresses[1]), "10.0.0.1")


if __name__ == "__main__":
    unittest.main()
