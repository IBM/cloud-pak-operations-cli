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

from abc import ABC, abstractmethod


class AbstractCredentials(ABC):
    def __init__(self, server: str):
        """Manages OpenShift access tokens

        Parameters
        ----------
        server
            URL of the OpenShift server for which OAuth access tokens are managed
        """

        self._server = server

    @abstractmethod
    def get_access_token(self, force_refresh_if_possible: bool = False) -> str:
        """Returns the current OAuth access token or obtains one from the
        OpenShift server passed to the constructor if possible

        Parameters
        ----------
        force_refresh_if_possible
            flag indicating whether a fresh OAuth access token shall be obtained

        Returns
        -------
        str
            OAuth access token
        """

        pass

    def get_server(self) -> str:
        """Returns the URL of the OpenShift server for which OAuth access tokens
        are managed

        Returns
        -------
        str
            URL of the OpenShift server for which OAuth access tokens are managed
        """

        return self._server

    @abstractmethod
    def is_refreshable(self) -> bool:
        """Returns whether the current OAuth access token can be refreshed

        Returns
        -------
        bool
            true, if the current OAuth access token can be refreshed
        """

        pass

    @abstractmethod
    def persist_access_token(self, token: str):
        """Persists a refreshed access token"""
        pass

    @abstractmethod
    def refresh_access_token(self):
        """Refreshes the current OAuth access token if possible"""

        pass
