#  Copyright 2021, 2022 IBM Corporation
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

import platform

from enum import Enum


class OperatingSystem(Enum):
    LINUX_X86_64 = 1
    MAC_OS = 2
    WINDOWS = 3


def get_operating_system():
    """Returns the operating system

    Returns
    -------
    OperatingSystem
        operating system
    """

    machine = platform.machine()
    result: OperatingSystem
    system = platform.system()

    if system == "Darwin":
        result = OperatingSystem.MAC_OS
    elif system == "Linux":
        if machine == "x86_64":
            result = OperatingSystem.LINUX_X86_64
        else:
            raise ValueError("Unsupported Linux architecture: " + machine)
    elif system == "Windows":
        if machine == "AMD64":
            result = OperatingSystem.WINDOWS
        else:
            raise ValueError("Unsupported Windows architecture: " + machine)
    else:
        raise ValueError("Unsupported platform: " + system)

    return result
