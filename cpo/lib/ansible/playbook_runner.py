#  Copyright 2022, 2023 IBM Corporation
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
import pathlib
import re as regex

from abc import ABC, abstractmethod
from typing import Any

import ansible_runner

from ansible_runner.runner import Runner
from ansible_runner.streaming import Processor, Transmitter, Worker

from cpo.config import configuration_manager
from cpo.utils.error import CloudPakOperationsCLIException

logger = logging.getLogger(__name__)


class PlaybookRunner(ABC):
    """Base class to be inherited by all playbook runners"""

    def __init__(self, playbook_name: str):
        self._playbook_name = playbook_name

    @abstractmethod
    def get_private_data_dir(self) -> pathlib.Path:
        """Returns the private data directory used by Ansible Runner

        Returns
        -------
        str
            private data directory used by Ansible Runner
        """

        return configuration_manager.get_deps_directory_path() / "playbooks"

    def run_playbook(self):
        """Runs a playbook"""

        runner = self._run_playbook()

        if runner.status == "failed":
            raise CloudPakOperationsCLIException("Ansible playbook failed")

    def _event_handler(self, event_data: Any):
        """Callback invoked by Ansible Runner in case Ansible Runner itself
        receives an event

        Parameters
        ----------
        event_data
            Ansible Runner event data
        """

        if ("stdout" in event_data) and (event_data["stdout"] != ""):
            if ("event" in event_data) and (event_data["event"] == "runner_on_failed"):
                logger.log(logging.ERROR, event_data["stdout"].removeprefix("\r\n"))
            else:
                logger.log(logging.DEBUG, event_data["stdout"].removeprefix("\r\n"))

    def _get_extra_vars(self) -> dict:
        """Returns extra vars/additional variables

        Returns
        -------
        dict
            dictionary of extra vars/additional variables
        """

        return self.__dict__

    def _get_playbook_name_from_class_name(self) -> str:
        """Returns the playbook name

        The playbook name is computed by removing the "Runner" suffix from the
        class name, converting the resulting string from camel case to snake
        case, and appending ".yml".

        Returns
        -------
        str
            playbook name
        """

        class_name_without_runner_suffix = self.__class__.__name__.removesuffix("Runner")
        # AAABbbbCccc → AAA_BbbbCccc
        class_name_using_snake_case = regex.sub("([0-9A-Z])([A-Z][a-z]+)", r"\1_\2", class_name_without_runner_suffix)
        # AAA_BbbbCccc → AAA_Bbbb_Cccc
        class_name_using_snake_case = regex.sub("([0-9a-z])([A-Z])", r"\1_\2", class_name_using_snake_case)
        # AAA_Bbbb_Cccc → aaa_bbbb_cccc.yml
        playbook_name = f"{class_name_using_snake_case}.yaml".lower()

        return playbook_name

    def _run_playbook(self) -> Processor | Runner | Transmitter | Worker:
        """Runs the playbook with the name passed in the constructor

        Returns
        -------
        Processor | Runner | Transmitter | Worker
            object returned by Ansible Runner for post-processing purposes"""

        runner = ansible_runner.run(
            artifact_dir=configuration_manager.get_cli_data_directory_path() / "artifacts",
            envvars={
                "ANSIBLE_JINJA2_NATIVE": True,
                "ANSIBLE_LIBRARY": configuration_manager.get_root_package_path() / "lib" / "ansible" / "modules",
            },
            extravars=self._sanitize_extra_vars(self._get_extra_vars()),
            event_handler=self._event_handler,
            playbook=self._playbook_name,
            private_data_dir=self.get_private_data_dir(),
            quiet=True,
            suppress_env_files=True,
        )

        return runner

    def _sanitize_extra_vars(self, extravars: dict) -> dict:
        """Sanitizes the given dictionary by removing pairs whose key starts
        with an underscore or whose value is None

        Parameters
        ----------
        extravars
            dictionary to be sanitized

        Returns
        -------
        dict
            sanitized dictionary
        """

        sanitized_extravars = {
            key: value for key, value in extravars.items() if not key.startswith("_") and (value is not None)
        }

        return sanitized_extravars
