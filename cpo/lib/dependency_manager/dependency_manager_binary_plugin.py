#  Copyright 2023, 2024 IBM Corporation
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

import os
import pathlib

from abc import abstractmethod

import semver

import cpo.utils.process

from cpo.config import configuration_manager
from cpo.lib.dependency_manager.dependency_manager_plugin import AbstractDependencyManagerPlugIn


class DependencyManagerBinaryPlugIn(AbstractDependencyManagerPlugIn):
    def execute_binary(
        self,
        version: semver.Version,
        args: list[str],
        env: dict[str, str] = os.environ.copy(),
        capture_output=False,
        check=True,
        print_captured_output=False,
    ) -> cpo.utils.process.ProcessResult:
        """Executes the binary associated with the dependency

        Parameters
        ----------
        version
            binary version
        args
            arguments to be passed to the binary
        env
            dictionary of environment variables passed to the process
        capture_output
            flag indicating whether process output shall be captured
        check
            flag indicating whether an exception shall be thrown if the binary
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

        binary_path = self.get_binary_path(version)

        return cpo.utils.process.execute_command(
            binary_path,
            args,
            env,
            capture_output=capture_output,
            check=check,
            print_captured_output=print_captured_output,
        )

    @abstractmethod
    def get_binary_name(self) -> str:
        """Returns the name of the binary associated with the dependency

        Returns
        -------
        str
            name of the binary associated with the dependency
        """

        pass

    def get_binary_path(self, version: semver.Version) -> pathlib.Path:
        """Returns the path of the binary associated with the dependency

        Parameters
        ----------
        version
            version of the dependency

        Returns
        -------
        pathlib.Path
            path of the binary associated with the dependency
        """

        binary_path = configuration_manager.get_bin_directory_path()

        if self.is_located_in_subdirectory():
            binary_path /= f"{self.get_dependency_alias()}-{version}"
            binary_path /= self.get_binary_name()
        else:
            binary_path /= f"{self.get_binary_name()}-{version}"

        return binary_path
