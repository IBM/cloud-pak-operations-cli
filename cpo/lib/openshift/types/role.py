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

from typing import TypedDict

from cpo.lib.openshift.types.object_meta import ObjectMeta
from cpo.lib.openshift.types.role_rule import RoleRule


class Role(TypedDict):
    """
    Notes
    -----
    https://docs.openshift.com/container-platform/latest/rest_api/rbac_apis/clusterrole-rbac-authorization-k8s-io-v1.html#clusterrole-rbac-authorization-k8s-io-v1
    https://docs.openshift.com/container-platform/latest/rest_api/rbac_apis/role-rbac-authorization-k8s-io-v1.html#role-rbac-authorization-k8s-io-v1
    """

    apiVersion: str
    kind: str
    metadata: ObjectMeta
    rules: list[RoleRule]
