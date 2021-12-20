#  Copyright 2021 IBM Corporation
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

import json
import pathlib
import re as regex

from abc import ABC, abstractmethod
from typing import List, Optional

import requests
import semver

import cpo.utils.process

from cpo.config import configuration_manager
from cpo.lib.error import DataGateCLIException


class AbstractDependencyManagerPlugIn(ABC):
    """Base class of all dependency manager plug-in classes"""

    @abstractmethod
    def download_dependency_version(self, version: semver.VersionInfo):
        """Downloads the given version of the dependency

        Parameters
        ----------
        version
            version of the dependency to be downloaded
        """

        pass

    def execute_binary(
        self, args: List[str], capture_output=False, check=True, print_captured_output=False
    ) -> cpo.utils.process.ProcessResult:
        """Executes the binary associated with the dependency

        If the dependency does not provide a binary, an exception is raised.

        Parameters
        ----------
        args
            arguments to be passed to the binary
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

        binary_path = self.get_binary_path()

        if binary_path is None:
            raise DataGateCLIException(f"Dependency '{self.get_dependency_name()} does not provide a binary'")

        return cpo.utils.process.execute_command(
            binary_path,
            args,
            capture_output=capture_output,
            check=check,
            print_captured_output=print_captured_output,
        )

    def get_binary_name(self) -> Optional[str]:
        """Returns the name of the binary associated with the dependency

        Returns
        -------
        Optional[str]
            name of the binary associated with the dependency or None if the
            dependency does not provide a binary
        """

        return None

    def get_binary_path(self) -> Optional[pathlib.Path]:
        """Returns the path of the binary associated with the dependency

        Returns
        -------
        Optional[pathlib.Path]
            path of the binary associated with the dependency or None if the
            dependency does not provide a binary
        """

        binary_name = self.get_binary_name()

        return configuration_manager.get_bin_directory_path() / binary_name if binary_name is not None else None

    @abstractmethod
    def get_dependency_alias(self) -> str:
        """Returns the alias of the dependency

        The alias is used as a key in ~/.cpo/binaries.json to store the version
        of the downloaded dependency.

        Example:

        {
            […]
            "ibmcloud": "1.2.3",
            […]
        }

        Returns
        -------
        str
            alias of the dependency
        """

        pass

    @abstractmethod
    def get_dependency_name(self) -> str:
        """Returns the dependency name

        Returns
        -------
        str
            dependency name
        """

        pass

    @abstractmethod
    def get_latest_dependency_version(self) -> semver.VersionInfo:
        """Returns the latest version of the dependency available at the
        official download location

        Returns
        -------
        semver.VersionInfo
            latest version of the dependency available at the official download
            location
        """

        pass

    def _get_latest_dependency_version_on_github(self, owner: str, repo: str) -> Optional[semver.VersionInfo]:
        """Returns the latest version of the dependency on GitHub

        This method parses the "name" key of the JSON document returned by the
        GitHub Releases API, which has the following structure:

        [
            {
                "url": […],
                "html_url": […],
                "assets_url": […],
                "upload_url": […],
                "tarball_url": […],
                "zipball_url": […],
                "id": […],
                "node_id": […],
                "tag_name": […],
                "target_commitish": […],
                "name": "v1.0.0",
                "body": […],
                "draft": […],
                "prerelease": […],
                "created_at": […],
                "published_at": […],
                "author": {
                    […]
                },
                "assets": [
                    […]
                ]
            },
            {
                […]
                "name": "v2.0.0",
                […]
            },
            […]
        ]

        GitHub Releases API: https://developer.github.com/v3/repos/releases/

        Parameters
        ----------
        owner
            GitHub repository owner
        repo
            GitHub repository name

        Returns
        -------
        Optional[semver.VersionInfo]
            latest version of the dependency or None if no release was found
        """

        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
        response.raise_for_status()

        response_json = json.loads(response.content)
        result: Optional[semver.VersionInfo] = None

        for release in response_json:
            search_result = regex.search(
                "v(\\d+\\.\\d+\\.\\d+)$",
                release["name"],
            )

            if search_result is not None:
                result = semver.VersionInfo.parse(search_result.group(1))

                break

        return result
