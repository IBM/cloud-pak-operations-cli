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

from abc import ABC, abstractmethod
from typing import Any, Dict

ClusterData = Dict[str, Any]


class AbstractCluster(ABC):
    def __init__(self, server: str, cluster_data: ClusterData):
        self.cluster_data = cluster_data
        self.server = server

    @abstractmethod
    def get_cluster_access_token(self) -> str:
        pass

    def get_cluster_data(self) -> ClusterData:
        return self.cluster_data

    def get_server(self) -> str:
        return self.server

    @abstractmethod
    def login(self):
        pass
