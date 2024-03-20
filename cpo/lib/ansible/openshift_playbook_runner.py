#  Copyright 2022, 2024 IBM Corporation
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

import logging

from typing import Any, Optional

import jmespath

import cpo.lib.jmespath

from cpo.config import configuration_manager
from cpo.lib.ansible.playbook_runner import PlaybookRunner
from cpo.lib.openshift.credentials.credentials import AbstractCredentials
from cpo.lib.openshift.openshift_api_manager import OpenShiftAPIManager
from cpo.utils.error import CloudPakOperationsCLIException

logger = logging.getLogger(__name__)


class OpenShiftPlaybookRunner(PlaybookRunner):
    """Base class to be inherited by all OpenShift-based playbook runners"""

    def __init__(
        self,
        playbook_name: str,
        credentials: AbstractCredentials,
        *,
        private_data_dir=configuration_manager.get_deps_directory_path() / "playbooks",
        variables: dict[str, Any] = {},
    ):
        super().__init__(playbook_name, private_data_dir=private_data_dir, variables=variables)

        self._openshift_api_manager = OpenShiftAPIManager(credentials)
        self._token_expired = False
        self.kube_config: Optional[dict[str, Any]] = None

    # override
    def run_playbook(self):
        """Runs a playbook

        If the OpenShift-based playbook fails due to an expired OAuth access
        token, it is refreshed an the playbook is rerun.
        """

        self.kube_config = self._openshift_api_manager.get_kube_config()

        runner = self._run_playbook()

        if runner.status == "failed":
            if self._token_expired:
                logger.log(logging.INFO, "Refreshing OAuth access token …")
                self._openshift_api_manager.refresh_access_token()
                self.kube_config = self._openshift_api_manager.get_kube_config()

                runner = self._run_playbook()

                if runner.status == "failed":
                    raise CloudPakOperationsCLIException("Ansible playbook failed")
            else:
                raise CloudPakOperationsCLIException("Ansible playbook failed")

    # override
    def _event_handler(self, event_data: Any):
        try:
            event = cpo.lib.jmespath.get_jmespath_string("event", event_data)

            if (event == "runner_on_failed") and self._check_if_unauthorized(event_data):
                self._token_expired = True
        except cpo.lib.jmespath.JmespathPathExpressionNotFoundException:
            pass

        super()._event_handler(event_data)

    def _check_if_unauthorized(self, event_data: Any) -> bool:
        unauthorized = jmespath.search("event_data.res.reason", event_data) == "Unauthorized"

        if not unauthorized:
            msg = cpo.lib.jmespath.get_jmespath_string("event_data.res.msg", event_data)

            unauthorized = msg.startswith("Exception '401\nReason: Unauthorized") or (
                (msg == "MODULE FAILURE\nSee stdout/stderr for the exact error")
                and (
                    "kubernetes.dynamic.exceptions.UnauthorizedError: 401\nReason: Unauthorized"
                    in cpo.lib.jmespath.get_jmespath_string("event_data.res.module_stderr", event_data)
                )
            )

        return unauthorized
