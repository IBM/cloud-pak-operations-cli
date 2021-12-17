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
import re as regex

from typing import List, Optional

from cpo.lib.error import DataGateCLIException


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
