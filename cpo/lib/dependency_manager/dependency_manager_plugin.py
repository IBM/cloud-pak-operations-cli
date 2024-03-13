#  Copyright 2021, 2024 IBM Corporation
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
import re as regex

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
import semver

from cpo.utils.error import CloudPakOperationsCLIException
from cpo.utils.operating_system import OperatingSystem


@dataclass
class DependencyVersion:
    version: semver.Version
    version_string: str | None = None

    def __str__(self) -> str:
        return str(self.version)


class AbstractDependencyManagerPlugIn(ABC):
    """Base class of all dependency manager plug-in classes"""

    @classmethod
    def parse_as_semantic_version(cls, version_number: str) -> DependencyVersion:
        """Parses the given version number string as a semantic version

        If the given string is a version number containing a major, minor, and
        patch version, leading zeros of each version are stripped before parsing
        the version number as a semantic version.

        Parameters
        ----------
            version
                version number string

        Returns
        -------
            DependencyVersion
                dependency version based on the parsed version number string
        """

        search_result = regex.search("v(\\d+)\\.(\\d+)\\.(\\d+)$", version_number)

        if search_result is None:
            raise CloudPakOperationsCLIException(f"String could not be parsed as semantic version: {version_number}")

        major = search_result.group(1) if search_result.group(1) == "0" else search_result.group(1).lstrip("0")
        minor = search_result.group(2) if search_result.group(2) == "0" else search_result.group(2).lstrip("0")
        patch = search_result.group(3) if search_result.group(3) == "0" else search_result.group(3).lstrip("0")

        return DependencyVersion(
            semver.Version.parse(f"{major}.{minor}.{patch}"),
            f"{search_result.group(1)}.{search_result.group(2)}.{search_result.group(3)}",
        )

    @abstractmethod
    def download_dependency_version(self, dependency_version: DependencyVersion):
        """Downloads the given version of the dependency

        Parameters
        ----------
        dependency_version
            version of the dependency to be downloaded
        """

        pass

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
    def get_latest_dependency_version(self) -> DependencyVersion:
        """Returns the latest version of the dependency available at the
        official download location

        Returns
        -------
        DependencyVersion
            latest version of the dependency available at the official download
            location
        """

        pass

    @abstractmethod
    def is_operating_system_supported(self, operating_system: OperatingSystem) -> bool:
        pass

    def _get_latest_dependency_version_on_github(self, owner: str, repo: str) -> Optional[DependencyVersion]:
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
        Optional[DependencyVersion]
            latest version of the dependency or None if no release was found
        """

        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
        response.raise_for_status()

        response_json = json.loads(response.content)
        result: Optional[DependencyVersion] = None

        if len(response_json) != 0:
            result = AbstractDependencyManagerPlugIn.parse_as_semantic_version(response_json[0]["name"])

        return result
