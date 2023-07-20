#  Copyright 2021, 2023 IBM Corporation
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

import netifaces
import urllib3
import urllib3.exceptions


class ScopedInsecureRequestWarningDisabler:
    """Temporarily disables warnings of type InsecureRequestWarning"""

    def __init__(self, enabled=True):
        self._enabled = enabled
        self._previously_disabled = False

        if enabled:
            for filter in warnings.filters:
                if filter[2] == urllib3.exceptions.InsecureRequestWarning:
                    self._previously_disabled = filter[0] == "ignore"

                    break

    def __enter__(self):
        if self._enabled and not self._previously_disabled:
            # disable warning:
            # InsecureRequestWarning: Unverified HTTPS request is being made to host
            # '…'. Adding certificate verification is strongly advised. See:
            # https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def __exit__(self, exc_type, exc_value, traceback):
        if self._enabled and not self._previously_disabled:
            warnings.simplefilter("always", urllib3.exceptions.InsecureRequestWarning)


def disable_insecure_request_warning():
    """Disables InsecureRequestWarning"""

    # disable warning:
    # InsecureRequestWarning: Unverified HTTPS request is being made to host
    # '…'. Adding certificate verification is strongly advised. See:
    # https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_local_ipv4_addresses() -> list[ipaddress.IPv4Address]:
    """Returns all IPv4 addresses bound to local network interfaces

    Returns
    -------
    list[ipaddress.IPv4Address]
        all IPv4 addresses bound to local network interfaces
    """

    result: list[ipaddress.IPv4Address] = []

    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)

        if netifaces.AF_INET in ifaddresses:
            # IPv4 address is bound to NIC
            ifaddress = ifaddresses[netifaces.AF_INET][0]

            ip_address = ipaddress.ip_address(ifaddress["addr"])

            if isinstance(ip_address, ipaddress.IPv4Address):
                result.append(ip_address)

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


def parse_hostname_result(hostname_result: str) -> list[ipaddress.IPv4Address]:
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

    hostnames = hostname_result.rstrip().split(" ")
    ip_addresses = list(map(lambda str: ipaddress.ip_address(str), hostnames))
    ipv4_addresses: list[ipaddress.IPv4Address] = []

    for ip_address in ip_addresses:
        if isinstance(ip_address, ipaddress.IPv4Address):
            ipv4_addresses.append(ip_address)

    return ipv4_addresses
