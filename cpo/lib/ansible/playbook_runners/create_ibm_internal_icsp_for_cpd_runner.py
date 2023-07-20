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

import pathlib

from cpo.lib.ansible.openshift_playbook_runner import OpenShiftPlaybookRunner
from cpo.lib.openshift.credentials.credentials import AbstractCredentials


class CreateIBMInternalICSPForCPDRunner(OpenShiftPlaybookRunner):
    def __init__(self, credentials: AbstractCredentials):
        super().__init__(self._get_playbook_name_from_class_name(), credentials)

    def get_private_data_dir(self) -> pathlib.Path:
        return super().get_private_data_dir()
