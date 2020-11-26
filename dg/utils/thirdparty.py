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

import logging
import pathlib

from subprocess import CalledProcessError, CompletedProcess, Popen, run
from typing import Final

from dg.config import DataGateConfigurationManager

IBM_CLOUD_PATH: Final[
    pathlib.Path
] = DataGateConfigurationManager().get_ibmcloud_cli_path()

OC_PATH: Final[pathlib.Path] = DataGateConfigurationManager().get_oc_cli_path()


def execute_ibmcloud_command(
    command: list[str], check: bool = False, timeout: int = None
) -> CompletedProcess:
    return _execute_command(str(IBM_CLOUD_PATH), command, check, timeout)


def execute_ibmcloud_command_with_check(command: list[str]) -> CompletedProcess:
    return execute_ibmcloud_command(command, check=True)


def execute_ibmcloud_command_interactively(command: list[str]) -> int:
    command = [
        str(IBM_CLOUD_PATH),
    ] + command
    proc = Popen(command)
    proc.communicate()
    return proc.returncode


def execute_oc_command(
    command: list[str], check: bool = False, timeout: int = None
) -> CompletedProcess:
    return _execute_command(str(OC_PATH), command, check, timeout)


def execute_oc_command_with_check(command: list[str]) -> CompletedProcess:
    return execute_oc_command(command, check=True)


def _execute_command(
    program: str, command: list[str], check: bool = False, timeout: int = None
) -> CompletedProcess:

    args = [program] + command

    logging.info(f"Executing command: {' '.join(args)}")

    command_result = None
    try:
        command_result = run(
            args,
            check=check,
            timeout=timeout,
            capture_output=True,
            text=True,
        )
    except CalledProcessError as error:
        print(f"Command '{error.cmd}' failed with return code {error.returncode}:")
        print(error.stdout)
        print(error.stderr)
        raise

    return command_result
