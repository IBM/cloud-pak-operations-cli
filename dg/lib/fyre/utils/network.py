import ipaddress
import re as regex

from typing import List, Optional

from dg.lib.error import DataGateCLIException


def get_private_ip_address_of_infrastructure_node(ipv4_addresses: List[ipaddress.IPv4Address]) -> ipaddress.IPv4Address:
    """Returns the private IP address of the infrastructure node

    Parameters
    ----------
    ipv4_addresses
        all IPv4 addresses bound to local network interfaces of the
        infrastructure node

    Returns
    -------
    ipaddress.IPv4Address
        private IP address of the infrastructure node
    """

    result: Optional[ipaddress.IPv4Address] = None

    for ipv4_address in ipv4_addresses:
        search_result = regex.match("(10\\.\\d+\\.\\d+\\.\\d+)", str(ipv4_address))

        if search_result is not None:
            result = ipv4_address

            break

    if result is None:
        raise DataGateCLIException("Private IP address not found")

    return result
