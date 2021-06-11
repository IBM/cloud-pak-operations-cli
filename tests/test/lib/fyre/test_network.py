import ipaddress
import unittest

import dg.lib.fyre.utils.network
import dg.utils.network


class TestNetworkUtilities(unittest.TestCase):
    def test_get_private_ip_address_of_infrastructure_node(self):
        """Tests dg.utils.network.is_hostname_localhost()"""

        hostname_result = "9.0.0.1 10.0.0.1"
        ipv4_addresses = dg.utils.network.parse_hostname_result(hostname_result)

        self.assertEqual(
            dg.lib.fyre.utils.network.get_private_ip_address_of_infrastructure_node(ipv4_addresses),
            ipaddress.ip_address("10.0.0.1"),
        )


if __name__ == "__main__":
    unittest.main()
