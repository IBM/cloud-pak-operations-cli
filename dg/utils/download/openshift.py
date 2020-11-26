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

import urllib.parse

from typing import Final

import dg.config
import dg.utils.compression
import dg.utils.download
import dg.utils.file
import dg.utils.operating_system

from dg.utils.operating_system import OperatingSystem

OPENSHIFT_CLI_DOWNLOAD_URL: Final[
    str
] = "https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/{}/{}"


def download_openshift_container_platform_cli():
    """Downloads the latest OpenShift Container Platform CLI version"""

    operating_system = dg.utils.operating_system.get_operating_system()
    operating_system_file_name_pattern_dict = {
        OperatingSystem.LINUX_X86_64: {"directory": "linux", "extension": "tar.gz"},
        OperatingSystem.MAC_OS: {"directory": "macosx", "extension": "tar.gz"},
        OperatingSystem.WINDOWS: {"directory": "windows", "extension": "zip"},
    }

    directory_name = operating_system_file_name_pattern_dict[operating_system][
        "directory"
    ]

    file_name = "oc.{}".format(
        operating_system_file_name_pattern_dict[operating_system]["extension"]
    )

    url = OPENSHIFT_CLI_DOWNLOAD_URL.format(
        directory_name,
        file_name,
    )

    archive_path = dg.utils.download.download_file(urllib.parse.urlsplit(url))

    target_directory_path = (
        dg.config.data_gate_configuration_manager.get_dg_bin_directory_path()
    )

    dg.utils.compression.extract_archive(archive_path, target_directory_path)
