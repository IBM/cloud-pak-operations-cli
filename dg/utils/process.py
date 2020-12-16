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
import subprocess


def execute_command(program: pathlib.Path, args: list[str]) -> subprocess.CompletedProcess:
    command = [str(program)] + args

    logging.info(f"Executing command: {' '.join(command)}")

    completed_process = subprocess.run(command, capture_output=True, text=True)

    if completed_process.returncode != 0:
        command_string = " ".join(command)
        error_output = ""

        if completed_process.stderr != "":
            error_output = f' ("{completed_process.stderr.rstrip()}")'

        raise Exception(
            f"Command '{command_string}' failed with return code {completed_process.returncode}{error_output}"
        )

    return completed_process


def execute_command_without_check(program: pathlib.Path, args: list[str]) -> subprocess.CompletedProcess:
    command = [str(program)] + args

    logging.info(f"Executing command: {' '.join(command)}")

    completed_process = subprocess.run(command, capture_output=True, text=True)

    return completed_process
