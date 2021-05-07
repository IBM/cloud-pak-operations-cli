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

from typing import List, Type

from dg.config.binaries_manager import binaries_manager
from dg.lib.download_manager.download_manager_plugin import (
    AbstractDownloadManagerPlugIn,
)


class DownloadManager:
    """Responsible for downloading dependencies"""

    def __init__(self):
        self._download_manager_plugins: List[AbstractDownloadManagerPlugIn] = []

    def register_plugin(self, cls: Type[AbstractDownloadManagerPlugIn]):
        """Registers a download manager plug-in responsible for downloading a
        specific dependency

        Parameters
        ----------
        cls
            Type of the download manager plug-in to be registered
        """

        self._download_manager_plugins.append(cls())

    def download_dependencies_if_required(self):
        """Downloads dependencies if required

        The versions of the downloaded dependencies are stored in
        ~/.dg/binaries.json.
        """

        for download_manager_plugin in self._download_manager_plugins:
            binary_alias = download_manager_plugin.get_binary_alias()
            current_version = binaries_manager.get_binary_version(binary_alias)
            latest_version = download_manager_plugin.get_latest_binary_version()

            if (current_version is None) or (latest_version.compare(current_version) == 1):
                download_manager_plugin.download_binary_version(latest_version)
                binaries_manager.set_binary_version(binary_alias, str(latest_version))
