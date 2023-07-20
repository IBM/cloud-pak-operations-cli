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

import asyncio
import logging
import os
import pathlib

from typing import Callable, Optional

import click

from cpo.utils.error import CloudPakOperationsCLIException


class ProcessResult:
    def __init__(self, command: list[str], return_code: int, stderr: list[str], stdout: list[str]):
        self.command = command
        self.return_code = return_code
        self._stderr = stderr
        self._stdout = stdout

    def raise_for_status(self):
        if self.return_code != 0:
            command_string = " ".join(self.command)

            raise CloudPakOperationsCLIException(
                f"Command '{command_string}' failed with return code {self.return_code}.",
                self.stderr,
                self.stdout,
            )

    @property
    def stderr(self) -> str:
        return "\n".join(self._stderr)

    @property
    def stdout(self) -> str:
        return "\n".join(self._stdout)


def execute_command(
    program: pathlib.Path,
    args: list[str],
    env: dict[str, str] = os.environ.copy(),
    capture_output=False,
    check=True,
    print_captured_output=False,
) -> ProcessResult:
    """Executes a process

    Parameters
    ----------
    program
        path of the executable
    args
        arguments to be passed to the executable
    env
        dictionary of environment variables passed to the process
    capture_output
        flag indicating whether process output shall be captured
    check
        flag indicating whether an exception shall be thrown if the executable
        returns with a nonzero return code
    print_captured_output
        flag indicating whether captured process output shall also be written to
        stdout/stderr

    Returns
    -------
    ProcessResult
        object storing the return code and captured process output (if
        requested)
    """

    command = [str(program)] + args

    logging.debug(f"Executing command: {' '.join(command)}")

    return_code: Optional[int] = None
    stderr_buffer: list[str] = []
    stdout_buffer: list[str] = []

    if capture_output:
        return_code = asyncio.run(
            _create_subprocess_and_capture_output(
                program,
                args,
                env,
                lambda line: _process_stdout_output(line, stdout_buffer, print_captured_output),
                lambda line: _process_stderr_output(line, stderr_buffer, print_captured_output),
            )
        )
    else:
        return_code = asyncio.run(_create_subprocess(program, args, env))

    result = ProcessResult(command, return_code, stderr_buffer, stdout_buffer)

    if check:
        result.raise_for_status()

    return result


def execute_command_without_check(
    program: pathlib.Path, args: list[str], capture_output=True, print_captured_output=False
) -> ProcessResult:
    """Executes a process without checking its return code

    Parameters
    ----------
    program
        path of the executable
    args
        arguments to be passed to the executable
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

    return execute_command(
        program,
        args,
        capture_output=capture_output,
        check=False,
        print_captured_output=print_captured_output,
    )


async def _create_subprocess(program: pathlib.Path, args: list[str], env: dict[str, str]) -> int:
    """Executes a process

    Parameters
    ----------
    program
        path of the executable
    args
        arguments to be passed to the executable
    env
        dictionary of environment variables passed to the process

    Returns
    -------
    int
        return code
    """

    process = await asyncio.create_subprocess_exec(*([str(program)] + args), env=env)

    return await process.wait()


async def _create_subprocess_and_capture_output(
    program: pathlib.Path, args: list[str], env: dict[str, str], stdout_callback, stderr_callback
) -> int:
    """Executes a process and captures its output to stdout/stderr

    Parameters
    ----------
    program
        path of the executable
    args
        arguments to be passed to the executable
    env
        dictionary of environment variables passed to the process
    stdout_callback
        callback invoked when a line was read from stdout
    stderr_callback
        callback invoked when a line was read from stderr

    Returns
    -------
    int
        return code
    """

    process = await asyncio.create_subprocess_exec(
        *([str(program)] + args),
        env=env,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )

    await asyncio.wait(
        [
            asyncio.create_task(_read_stream(process.stderr, stderr_callback)),
            asyncio.create_task(_read_stream(process.stdout, stdout_callback)),
        ]
    )

    return await process.wait()


def _process_stderr_output(line: str, buffer: list[str], print_captured_output: bool):
    if print_captured_output:
        click.echo(click.style(line, fg="red"), err=True, nl=False)

    buffer.append(line.rstrip())


def _process_stdout_output(line: str, buffer: list[str], print_captured_output: bool):
    if print_captured_output:
        click.echo(line, nl=False)

    buffer.append(line.rstrip())


async def _read_stream(stream: Optional[asyncio.StreamReader], callback: Callable[[str], None]):
    if stream is not None:
        while True:
            if len(line := await stream.readline()) != 0:
                callback(line.decode())
            else:
                break
