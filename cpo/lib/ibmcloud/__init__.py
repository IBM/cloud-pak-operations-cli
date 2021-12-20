#  Copyright 2020, 2021 IBM Corporation
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

import subprocess

from typing import Final, List

import cpo.utils.process

from cpo.lib.dependency_manager import dependency_manager
from cpo.lib.dependency_manager.plugins.ibm_cloud_cli_plugin import (
    IBMCloudCLIPlugIn,
)

EXTERNAL_IBM_CLOUD_API_KEY_NAME: Final[str] = "cloud-pak-operations-cli"
INTERNAL_IBM_CLOUD_API_KEY_NAME: Final[str] = "ibm_cloud_api_key"


def execute_ibmcloud_command(
    args: List[str], capture_output=False, check=True, print_captured_output=False
) -> cpo.utils.process.ProcessResult:
    """Executes the IBM Cloud CLI

    Parameters
    ----------
    args
        arguments to be passed to the IBM Cloud CLI
    capture_output
        flag indicating whether process output shall be captured
    check
        flag indicating whether an exception shall be thrown if the IBM Cloud
        CLI returns with a nonzero return code
    print_captured_output
        flag indicating whether captured process output shall also be written to
        stdout/stderr

    Returns
    -------
    ProcessResult
        object storing the return code and captured process output (if
        requested)
    """

    return dependency_manager.execute_binary(IBMCloudCLIPlugIn, args, capture_output, check, print_captured_output)


def execute_ibmcloud_command_interactively(args: List[str]) -> int:
    proc = subprocess.Popen(
        [
            str(dependency_manager.get_binary_path(IBMCloudCLIPlugIn)),
        ]
        + args
    )

    proc.communicate()

    return proc.returncode


def execute_ibmcloud_command_without_check(
    args: List[str], capture_output=False, print_captured_output=False
) -> cpo.utils.process.ProcessResult:
    """Executes the IBM Cloud CLI without checking its return code

    Parameters
    ----------
    args
        arguments to be passed to the IBM Cloud CLI
    capture_output
        flag indicating whether process output shall be captured
    print_captured_output
        flag indicating whether captured process output shall also be written to
        stdout/stderr

    Returns
    -------
    ProcessResult
        object storing the return code and captured process output (if
        requested)
    """

    return execute_ibmcloud_command(
        args,
        capture_output=capture_output,
        check=False,
        print_captured_output=print_captured_output,
    )
