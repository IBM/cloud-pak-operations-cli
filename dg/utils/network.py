#  Copyright 2020 IBM Corporation
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
import socket
import warnings

from typing import List

import netifaces
import urllib3


def disable_insecure_request_warning():
    """Disables InsecureRequestWarning"""

    # disable warning:
    # InsecureRequestWarning: Unverified HTTPS request is being made to host
    # '…'. Adding certificate verification is strongly advised. See:
    # https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def enable_insecure_request_warning():
    """Ensables InsecureRequestWarning"""

    warnings.simplefilter("always", urllib3.exceptions.InsecureRequestWarning)


def get_local_ipv4_addresses() -> List[ipaddress.IPv4Address]:
    """Returns all IPv4 addresses bound to local network interfaces

    Returns
    -------
    list[ipaddress.IPv4Address]
        all IPv4 addresses bound to local network interfaces
    """

    result: List[ipaddress.IPv4Address] = []

    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)

        if netifaces.AF_INET in ifaddresses:
            # IPv4 address is bound to NIC
            ifaddress = ifaddresses[netifaces.AF_INET][0]

            result.append(ipaddress.ip_address(ifaddress["addr"]))

    result.sort()

    return result


def is_hostname_localhost(hostname: str) -> bool:
    """Returns whether the IPv4 address associated with the given hostname
    is bound to one of the local network interfaces

    Parameters
    ----------
    hostname
        hostname to be checked

    Returns
    -------
    bool
        true, if the IPv4 address associated with the given hostname is bound to
        one of the local network interfaces
    """

    ipv4_address = ipaddress.ip_address(socket.gethostbyname(hostname))
    local_ipv4_addresses = get_local_ipv4_addresses()

    return ipv4_address in local_ipv4_addresses


def parse_hostname_result(hostname_result: str) -> List[ipaddress.IPv4Address]:
    """Parses the output of the hostname command (Linux)

    Parameters
    ----------
    hostname_result
        output of the hostname command (Linux)

    Returns
    -------
    list[ipaddress.IPv4Address]
        all IPv4 addresses bound to local network interfaces
    """

    hostname_result_list = hostname_result.rstrip().split(" ")
    ipv4_addresses: List[ipaddress.IPv4Address] = list(map(lambda str: ipaddress.ip_address(str), hostname_result_list))

    return ipv4_addresses
