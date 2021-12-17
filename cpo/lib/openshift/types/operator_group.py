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

from typing import List, TypedDict

from cpo.lib.openshift.types.object_meta import ObjectMeta


class OperatorGroupSpec(TypedDict):
    targetNamespaces: List[str]


class OperatorGroup(TypedDict):
    """
    Notes
    -----
    https://docs.openshift.com/container-platform/latest/rest_api/operatorhub_apis/operatorgroup-operators-coreos-com-v1.html#operatorgroup-operators-coreos-com-v1
    """

    apiVersion: str
    kind: str
    metadata: ObjectMeta
    spec: OperatorGroupSpec
