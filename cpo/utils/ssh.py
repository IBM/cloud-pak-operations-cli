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

import logging
import pathlib

from typing import Optional, Type

import asyncssh
import click
import colorama

from cpo.lib.error import DataGateCLIException

asyncssh.set_log_level(logging.WARNING)


class RemoteClient:
    """Class providing basic SSH functionality based on the asyncssh
    package"""

    def __init__(self, hostname: str):
        """Constructor

        Parameters
        ----------
        hostname
            name of the remote host to which an SSH connection shall be established
        """

        self._connection: Optional[asyncssh.SSHClientConnection] = None
        self._hostname = hostname

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.disconnect()

    async def connect(self):
        """Connects to the remote host"""

        self._connection = await asyncssh.connect(self._hostname, username="root")  # type: ignore

    async def disconnect(self):
        """Disconnects from the remote host"""

        if self._connection is not None:
            self._connection.close()

            await self._connection.wait_closed()

            self._connection = None

    async def execute(self, command: str, print_output: bool = True) -> str:
        """Executes the given command on the remote host

        Parameters
        ----------
        command
            command to execute on the remote host
        print_output
            flag indicating whether output to stdout and stderr of the command
            executed on the remote host shall be printed to stdout and stderr on the
            local host
        """

        logging.info(f"Executing command on {self._hostname}: {command}")

        if self._connection is None:
            raise DataGateCLIException("Not connected to " + self._hostname)

        channel, session = await self._connection.create_session(
            create_remote_client_ssh_session(print_output), command
        )

        await channel.wait_closed()
        session.check_exit_status()

        return session.get_received_data()

    async def upload(self, path: pathlib.Path):
        """Uploads a file to the remote host

        Parameters
        ----------
        path
            path of the file to be uploaded
        """

        if self._connection is None:
            raise DataGateCLIException("Not connected to " + self._hostname)

        await asyncssh.scp(str(path), self._connection)


def create_remote_client_ssh_session(print_output: bool) -> Type[asyncssh.SSHClientSession]:
    """Returns a parameterized subclass of asyncssh.SSHClientSession that
    may be passed to asyncssh.SSHClientConnection.create_session()

    Parameters
    ----------
    print_output
        flag indicating whether output to stdout and stderr of a command
        executed on a remote host shall be printed to stdout and stderr on the
        local host

    Returns
    -------
    RemoteClientSSHSession
        parameterized subclass of asyncssh.SSHClientSession
    """

    class RemoteClientSSHSession(asyncssh.SSHClientSession):
        """Class extending the asyncssh.SSHClientSession class

        This class extends the asyncssh.SSHClientSession class as follows:

        - Output to stderr of a command executed on a remote host is highlighted
          in red.
        - Output to stdout and stderr of a command executed on a remote host is
          stored and may be returned by calling get_received_data().

          For unknown reasons, output to stdout and stderr is not
          interleaved although it should be:

          - https://github.com/ronf/asyncssh/issues/58
          - https://github.com/ronf/asyncssh/issues/231
        """

        def __init__(self):
            self._channel: Optional[asyncssh.SSHClientChannel] = None
            self._received_data = ""

        def check_exit_status(self):
            """Checks the exit status of a command executed on a remote host and
            raises an asyncssh.ProcessError exception if it is not 0"""

            if (self._channel is not None) and (self._channel.get_exit_status() != 0):
                raise asyncssh.ProcessError(
                    self._channel.get_environment(),
                    self._channel.get_command(),
                    self._channel.get_subsystem(),
                    self._channel.get_exit_status(),
                    self._channel.get_exit_signal(),
                    self._channel.get_returncode(),
                    "",
                    "",
                )

        def connection_made(self, channel: asyncssh.SSHClientChannel):
            """see asyncssh.SSHClientSession.connection_made()"""

            self._channel = channel

        def data_received(self, data, datatype):
            if datatype == asyncssh.EXTENDED_DATA_STDERR:
                self._received_data += data

                if print_output:
                    click.echo(
                        colorama.Fore.RED + data + colorama.Fore.RESET,
                        err=True,
                        nl=False,
                    )
            else:
                self._received_data += data

                if print_output:
                    click.echo(data, nl=False)

        def get_received_data(self) -> str:
            """see asyncssh.SSHClientSession.get_received_data()"""

            return self._received_data

    return RemoteClientSSHSession
