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

import json
import re

from abc import ABC, abstractmethod
from typing import Union

import requests
import semver


class AbstractDownloadManagerPlugIn(ABC):
    """Base class of all download manager plug-in classes"""

    @abstractmethod
    def download_binary_version(self, version: semver.VersionInfo):
        """Downloads the given version of a dependency

        Parameters
        ----------
        version
            version of a dependency to be downloaded
        """

        pass

    @abstractmethod
    def get_binary_alias(self) -> str:
        """Returns the alias of a dependency

        The alias is used as a key in ~/.dg/binaries.json to store the latest
        downloaded version.

        Returns
        -------
        str
            alias of a dependency
        """

        pass

    @abstractmethod
    def get_latest_binary_version(self) -> semver.VersionInfo:
        """Returns the latest version of a dependency

        Returns
        -------
        semver.VersionInfo
            latest version of a dependency
        """

        pass

    def _get_latest_binary_version_on_github(
        self, owner: str, repo: str
    ) -> Union[semver.VersionInfo, None]:
        """Returns the latest version of a dependency on GitHub

        GitHub Releases API: https://developer.github.com/v3/repos/releases/

        Parameters
        ----------
        owner
            GitHub repository owner
        repo
            GitHub repository name

        Returns
        -------
        Union[semver.VersionInfo, None]
            latest version of a dependency or None if no release was found
        """

        response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
        response.raise_for_status()

        response_json = json.loads(response.content)
        result: Union[semver.VersionInfo, None] = None

        for release in response_json:
            search_result = re.search(
                "v(\\d+\\.\\d+\\.\\d+)$",
                release["name"],
            )

            if search_result is not None:
                result = semver.VersionInfo.parse(search_result.group(1))

                break

        return result
