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

from dataclasses import dataclass
from typing import Any, TypedDict

from cpo.lib.openshift.types.object_meta import ObjectMeta


class CustomResourceDict(TypedDict):
    apiVersion: str
    kind: str
    metadata: ObjectMeta
    spec: dict[str, Any]


@dataclass
class CustomResource:
    group: str
    kind: str
    metadata: ObjectMeta
    spec: dict[str, Any]
    version: str

    def create_custom_resource_dict(self) -> CustomResourceDict:
        return {
            "apiVersion": f"{self.group}/{self.version}",
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec,
        }
