#  Copyright 2023 IBM Corporation
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

from typing import Optional

from cpo.lib.dependency_manager.plugins.openshift.openshift_plugin import AbstractOpenShiftPlugIn
from cpo.utils.operating_system import OperatingSystem


class OpenShiftCLIPlugIn(AbstractOpenShiftPlugIn):
    # override
    def get_binary_name(self) -> Optional[str]:
        return "oc"

    # override
    def get_dependency_alias(self) -> str:
        return "oc"

    # override
    def get_dependency_name(self) -> str:
        return "OpenShift CLI"

    # override
    def _get_operating_system_file_name_dict(self) -> dict[OperatingSystem, str]:
        return {
            OperatingSystem.LINUX_X86_64: "openshift-client-linux.tar.gz",
            OperatingSystem.MAC_OS: "openshift-client-mac.tar.gz",
            OperatingSystem.WINDOWS: "openshift-client-windows.zip",
        }
